function gcep(stackInfo)
% gcep: Go to Current Execution Point.
% This function opens your editor at the current execution point when your code is stopped,
% i.e. when the prompt is K>>
% Your editor's path is hard-coded in this function in the variable EDITOR_CMD
%
% Copyright (C) 2022-2023 Cyrille Bougot
% This file is covered by the GNU General Public License.

  % Command to call your editor:
  % - the first place holder is replaced by the full path of the file to be opened
  % - the second place holder is replaced by the line where the file should be opened
  % E.g.:
  % EDITOR_CMD = 'c:\\path\\to\\my\\editor.exe "%s":%s';
  EDITOR_CMD = strrep([getenv('userprofile') '\Documents\App\6pad++\6pad++.exe "%s":%s'], '\', '\\');
  
  pattern = "> In [^<]+(<a href=""matlab: opentoline\('(?<file>[^']+)',(?<line>\d+),(?<col>\d+)\)"">[^\n]*(\n|$)";
  match = regexp(stackInfo, pattern, 'names');
  cmd = sprintf(['start /b ' EDITOR_CMD], match.file, match.line);
  disp(cmd)
  system(cmd);
  
end
