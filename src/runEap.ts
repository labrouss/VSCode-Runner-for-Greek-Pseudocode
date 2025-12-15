import * as vscode from "vscode";
import * as path from "path";
import * as os from "os";
import { spawnSync } from "child_process";
import * as fs from "fs";

function commandExists(cmd: string): boolean {
  const result = spawnSync(cmd, ["--version"], {
    stdio: "ignore",
    shell: true
  });
  return result.status === 0;
}

export function runEapProgram(context: vscode.ExtensionContext) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage("No active editor.");
    return;
  }

  const filePath = editor.document.fileName;
  const extPath = context.extensionPath;
  const platform = os.platform();

  const interpreterDir = path.join(extPath, "interpreter");
  const pythonInterpreter = path.join(interpreterDir, "interpreter.py");

  let command: string;
  let args: string[];

  // 1️⃣ Prefer Python if available
  if (commandExists("python3")) {
    command = "python3";
    args = [pythonInterpreter, filePath];
  } else if (commandExists("python")) {
    command = "python";
    args = [pythonInterpreter, filePath];
  } else {
    // 2️⃣ Fallback to compiled binary
    if (platform === "win32") {
      command = path.join(interpreterDir, "interpreter-win.exe");
    } else {
      command = path.join(interpreterDir, "interpreter-linux");
    }

    if (!fs.existsSync(command)) {
      vscode.window.showErrorMessage(
        "No Python interpreter or compiled EAP interpreter found."
      );
      return;
    }

    args = [filePath];
  }

  const terminal = vscode.window.createTerminal("EAP Runner");
  terminal.show();

  terminal.sendText(`"${command}" ${args.map(a => `"${a}"`).join(" ")}`);
}

