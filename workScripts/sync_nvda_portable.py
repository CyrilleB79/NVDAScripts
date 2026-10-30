"""
Synchronize an NVDA source checkout with runtime files from an NVDA portable build.

This utility prepares an NVDA source tree so it can be run without performing a
full native build by copying the runtime files that are not present in the
repository.

This may be useful if you have no working installation of Visual Studio.

Usage:
	python syncPortableRuntime.py <portableNvdaPath> <repoRootPath> [--dry-run] [--verbose]

Arguments:
	portableNvdaPath
		Path to the root directory of an NVDA portable copy.

	repoRootPath
		Path to the root of the NVDA source repository.

Options:
	--dry-run
		Show the operations that would be performed without modifying any files.

	--verbose
		Show the operations that are performed.
"""

import argparse
import os
import shutil
import zipfile


def copyFile(srcPath: str, dstPath: str, dryRun: bool, verbose: bool) -> None:
	"""
	Copy a file.
	"""
	if verbose:
		print(f"[DRY RUN] Copy file: {srcPath} -> {dstPath}" if dryRun else f"Copy file: {srcPath} -> {dstPath}")

	if dryRun:
		return

	os.makedirs(os.path.dirname(dstPath), exist_ok=True)
	shutil.copy2(srcPath, dstPath)


def removeFile(srcPath: str, dryRun: bool, verbose: bool) -> None:
	"""
	Remove a file.
	"""
	if verbose:
		print(f"[DRY RUN] Remove file: {srcPath}" if dryRun else f"Remove file: {srcPath}")

	if dryRun:
		return

	os.remove(srcPath)


def copyDirReplace(srcPath: str, dstPath: str, dryRun: bool, verbose: bool) -> None:
	"""
	Replace a directory completely (destructive).
	"""
	if verbose:
		print(f"[DRY RUN] Replace directory: {srcPath} -> {dstPath}" if dryRun else f"Replace directory: {srcPath} -> {dstPath}")

	if dryRun:
		return

	if os.path.exists(dstPath):
		shutil.rmtree(dstPath)

	shutil.copytree(srcPath, dstPath)


def copyDirMerge(srcPath: str, dstPath: str, dryRun: bool, verbose: bool, excludePathList: list[str] | None = None) -> None:
	"""
	Copy directory contents without deleting existing files.
	Existing files are overwritten, missing files are preserved.
	"""
	if not excludePathList:
		excludePathList =[]
	for root, dirs, files in os.walk(srcPath):
		relativeRoot = os.path.relpath(root, srcPath)

		for fileName in files:
			srcFile = os.path.join(root, fileName)

			if relativeRoot == ".":
				relativePath = fileName
			else:
				relativePath = os.path.join(relativeRoot, fileName)
			if relativePath in excludePathList:
				continue

			dstFile = os.path.join(dstPath, relativePath)

			if verbose:
				print(f"[DRY RUN] Merge copy: {srcFile} -> {dstFile}" if dryRun else f"Merge copy: {srcFile} -> {dstFile}")

			if dryRun:
				continue

			os.makedirs(os.path.dirname(dstFile), exist_ok=True)
			shutil.copy2(srcFile, dstFile)


def copyVersionedLibFolder(portableNvdaPath: str, repoRootPath: str, dryRun: bool, verbose: bool) -> None:
	libPath = os.path.join(portableNvdaPath, "lib")

	if not os.path.isdir(libPath):
		raise RuntimeError("Missing lib folder")

	versionFolders = [
		name
		for name in os.listdir(libPath)
		if os.path.isdir(os.path.join(libPath, name))
	]

	if len(versionFolders) != 1:
		raise RuntimeError(f"Expected exactly one lib version folder, found {versionFolders}")

	srcPath = os.path.join(libPath, versionFolders[0])
	dstPath = os.path.join(repoRootPath, "source", "lib")

	copyDirMerge(srcPath, dstPath, dryRun, verbose)


def copyComInterfaces(portableNvdaPath: str, repoRootPath: str, dryRun: bool, verbose: bool) -> None:
	zipPath = os.path.join(portableNvdaPath, "library.zip")
	dstRoot = os.path.join(repoRootPath, "source", "comInterfaces")

	if verbose:
		print(f"[DRY RUN] copy comInterfaces from library.zip" if dryRun else "copy comInterfaces from library.zip")

	if dryRun:
		return

	skipMember = "comInterfaces/__init__.py"

	with zipfile.ZipFile(zipPath) as z:
		for member in z.namelist():
			if not member.startswith("comInterfaces/"):
				continue

			if member == skipMember:
				continue

			relativePath = member[len("comInterfaces/"):]
			if not relativePath or relativePath.endswith("/"):
				continue

			dstPath = os.path.join(dstRoot, relativePath)

			with z.open(member) as srcFile:
				os.makedirs(os.path.dirname(dstPath), exist_ok=True)
				with open(dstPath, "wb") as outFile:
					shutil.copyfileobj(srcFile, outFile)


def copyLouisFolder(portableNvdaPath: str, repoRootPath: str, dryRun: bool, verbose: bool) -> None:
	copyDirReplace(
		os.path.join(portableNvdaPath, "louis"),
		os.path.join(repoRootPath, "source", "louis"),
		dryRun,
		verbose
	)


def copyLouisInit(portableNvdaPath: str, repoRootPath: str, dryRun: bool, verbose: bool) -> None:
	zipPath = os.path.join(portableNvdaPath, "library.zip")
	memberName = "louis/__init__.pyc"
	dstPath = os.path.join(repoRootPath, "source", "louis", "__init__.pyc")

	if verbose:
		print(f"[DRY RUN] extract {memberName}" if dryRun else f"extract {memberName}")

	if dryRun:
		return

	with zipfile.ZipFile(zipPath) as z:
		with z.open(memberName) as srcFile:
			os.makedirs(os.path.dirname(dstPath), exist_ok=True)
			with open(dstPath, "wb") as outFile:
				shutil.copyfileobj(srcFile, outFile)


def copyBrailleDisplayDrivers(portableNvdaPath: str, repoRootPath: str, dryRun: bool, verbose: bool) -> None:
	copyDirMerge(
		os.path.join(portableNvdaPath, "brailleDisplayDrivers"),
		os.path.join(repoRootPath, "source", "brailleDisplayDrivers"),
		dryRun,
		verbose
	)


def copySynthDrivers(portableNvdaPath: str, repoRootPath: str, dryRun: bool, verbose: bool) -> None:
	copyDirMerge(
		os.path.join(portableNvdaPath, "synthDrivers"),
		os.path.join(repoRootPath, "source", "synthDrivers"),
		dryRun,
		verbose
	)


def syncPortableArtifacts(portableNvdaPath: str, repoRootPath: str, dryRun: bool, verbose: bool) -> None:
	sourcePath = os.path.join(repoRootPath, "source")

	for itemName in os.listdir(portableNvdaPath):
		srcPath = os.path.join(portableNvdaPath, itemName)

		if os.path.isfile(srcPath):
			if itemName.endswith(".dll"):
				copyFile(srcPath, os.path.join(sourcePath, itemName), dryRun, verbose)

		elif os.path.isdir(srcPath):
			if itemName == "documentation":
				copyDirMerge(
					srcPath,
					os.path.join(repoRootPath, "user_docs"),
					dryRun,
					verbose,
					excludePathList=["copying.txt"],
				)

			elif itemName == "locale":
				copyDirMerge(srcPath, os.path.join(sourcePath, "locale"), dryRun, verbose)


def validatePortableLayout(portableNvdaPath: str) -> None:
	if not os.path.isfile(os.path.join(portableNvdaPath, "library.zip")):
		raise RuntimeError("Missing library.zip")

	libPath = os.path.join(portableNvdaPath, "lib")

	if not os.path.isdir(libPath):
		raise RuntimeError("Missing lib folder")

	versionFolders = [
		name
		for name in os.listdir(libPath)
		if os.path.isdir(os.path.join(libPath, name))
	]

	if len(versionFolders) != 1:
		raise RuntimeError(f"Expected exactly one lib version folder, found {versionFolders}")


def parseArguments() -> argparse.Namespace:
	parser = argparse.ArgumentParser()
	parser.add_argument("portableNvdaPath")
	parser.add_argument("repoRootPath")
	parser.add_argument("--dry-run", action="store_true")
	parser.add_argument("--verbose", action="store_true")
	return parser.parse_args()


def main() -> None:
	args = parseArguments()
	# Force verbose also for dry run to be useful
	verbose = args.verbose or args.dry_run, 

	validatePortableLayout(args.portableNvdaPath)

	copyVersionedLibFolder(args.portableNvdaPath, args.repoRootPath, args.dry_run, verbose)
	copyComInterfaces(args.portableNvdaPath, args.repoRootPath, args.dry_run, verbose)
	copyLouisFolder(args.portableNvdaPath, args.repoRootPath, args.dry_run, verbose)
	copyLouisInit(args.portableNvdaPath, args.repoRootPath, args.dry_run, verbose)
	copyBrailleDisplayDrivers(args.portableNvdaPath, args.repoRootPath, args.dry_run, verbose)
	copySynthDrivers(args.portableNvdaPath, args.repoRootPath, args.dry_run, verbose)

	syncPortableArtifacts(args.portableNvdaPath, args.repoRootPath, args.dry_run, verbose)


if __name__ == "__main__":
	main()
