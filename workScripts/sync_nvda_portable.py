"""
Synchronize an NVDA source checkout with runtime files from an NVDA portable build.

This utility prepares an NVDA source tree so it can be run without performing a
full native build by copying the runtime files that are not present in the
repository.

This may be useful if you have no working installation of Visual Studio.

Usage:
	python syncPortableRuntime.py <portableNvdaPath> <repoRootPath> [--dry-run]

Arguments:
	portableNvdaPath
		Path to the root directory of an NVDA portable copy.

	repoRootPath
		Path to the root of the NVDA source repository.

Options:
	--dry-run
		Show the operations that would be performed without modifying any files.
"""

import argparse
import os
import shutil
import zipfile


def copyFile(srcPath: str, dstPath: str, dryRun: bool) -> None:
	"""
	Copy a file.
	"""
	if dryRun:
		print(f"[DRY RUN] Copy file: {srcPath} -> {dstPath}")
		return

	os.makedirs(os.path.dirname(dstPath), exist_ok=True)
	shutil.copy2(srcPath, dstPath)


def copyDirReplace(srcPath: str, dstPath: str, dryRun: bool) -> None:
	"""
	Replace a directory completely (destructive).
	"""
	if dryRun:
		print(f"[DRY RUN] Replace directory: {srcPath} -> {dstPath}")
		return

	if os.path.exists(dstPath):
		shutil.rmtree(dstPath)

	shutil.copytree(srcPath, dstPath)


def copyDirMerge(srcPath: str, dstPath: str, dryRun: bool) -> None:
	"""
	Copy directory contents without deleting existing files.
	Existing files are overwritten, missing files are preserved.
	"""
	for root, dirs, files in os.walk(srcPath):
		relativeRoot = os.path.relpath(root, srcPath)

		for fileName in files:
			srcFile = os.path.join(root, fileName)

			if relativeRoot == ".":
				relativePath = fileName
			else:
				relativePath = os.path.join(relativeRoot, fileName)

			dstFile = os.path.join(dstPath, relativePath)

			if dryRun:
				print(f"[DRY RUN] Merge copy: {srcFile} -> {dstFile}")
				continue

			os.makedirs(os.path.dirname(dstFile), exist_ok=True)
			shutil.copy2(srcFile, dstFile)


def copyVersionedLibFolder(portableNvdaPath: str, repoRootPath: str, dryRun: bool) -> None:
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

	copyDirMerge(srcPath, dstPath, dryRun)


def copyComInterfaces(portableNvdaPath: str, repoRootPath: str, dryRun: bool) -> None:
	zipPath = os.path.join(portableNvdaPath, "library.zip")
	dstRoot = os.path.join(repoRootPath, "source", "comInterfaces")

	if dryRun:
		print("[DRY RUN] copy comInterfaces from library.zip")
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


def copyLouisFolder(portableNvdaPath: str, repoRootPath: str, dryRun: bool) -> None:
	copyDirReplace(
		os.path.join(portableNvdaPath, "louis"),
		os.path.join(repoRootPath, "source", "louis"),
		dryRun
	)


def copyLouisInit(portableNvdaPath: str, repoRootPath: str, dryRun: bool) -> None:
	zipPath = os.path.join(portableNvdaPath, "library.zip")
	memberName = "louis/__init__.pyc"
	dstPath = os.path.join(repoRootPath, "source", "louis", "__init__.pyc")

	if dryRun:
		print(f"[DRY RUN] extract {memberName}")
		return

	with zipfile.ZipFile(zipPath) as z:
		with z.open(memberName) as srcFile:
			os.makedirs(os.path.dirname(dstPath), exist_ok=True)
			with open(dstPath, "wb") as outFile:
				shutil.copyfileobj(srcFile, outFile)


def copyBrailleDisplayDrivers(portableNvdaPath: str, repoRootPath: str, dryRun: bool) -> None:
	copyDirMerge(
		os.path.join(portableNvdaPath, "brailleDisplayDrivers"),
		os.path.join(repoRootPath, "source", "brailleDisplayDrivers"),
		dryRun
	)


def copySynthDrivers(portableNvdaPath: str, repoRootPath: str, dryRun: bool) -> None:
	copyDirMerge(
		os.path.join(portableNvdaPath, "synthDrivers"),
		os.path.join(repoRootPath, "source", "synthDrivers"),
		dryRun
	)


def syncPortableArtifacts(portableNvdaPath: str, repoRootPath: str, dryRun: bool) -> None:
	sourcePath = os.path.join(repoRootPath, "source")

	for itemName in os.listdir(portableNvdaPath):
		srcPath = os.path.join(portableNvdaPath, itemName)

		if os.path.isfile(srcPath):
			if itemName.endswith(".dll") or itemName.endswith(".pyd"):
				copyFile(srcPath, os.path.join(sourcePath, itemName), dryRun)

		elif os.path.isdir(srcPath):
			if itemName == "documentation":
				copyDirReplace(srcPath, os.path.join(repoRootPath, "user_docs"), dryRun)

			elif itemName == "locale":
				copyDirReplace(srcPath, os.path.join(sourcePath, "locale"), dryRun)


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
	return parser.parse_args()


def main() -> None:
	args = parseArguments()

	validatePortableLayout(args.portableNvdaPath)

	copyVersionedLibFolder(args.portableNvdaPath, args.repoRootPath, args.dry_run)
	copyComInterfaces(args.portableNvdaPath, args.repoRootPath, args.dry_run)
	copyLouisFolder(args.portableNvdaPath, args.repoRootPath, args.dry_run)
	copyLouisInit(args.portableNvdaPath, args.repoRootPath, args.dry_run)
	copyBrailleDisplayDrivers(args.portableNvdaPath, args.repoRootPath, args.dry_run)
	copySynthDrivers(args.portableNvdaPath, args.repoRootPath, args.dry_run)

	syncPortableArtifacts(args.portableNvdaPath, args.repoRootPath, args.dry_run)


if __name__ == "__main__":
	main()