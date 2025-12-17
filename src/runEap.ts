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

export async function runEapProgram(context: vscode.ExtensionContext) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage("Greek PseudoRun: No active editor found.");
    return;
  }
  if (editor.document.isDirty) {
        await editor.document.save();
  }

  const filePath = editor.document.fileName;
  const extPath = context.extensionPath;
  const platform = os.platform();

  const interpreterDir = path.join(extPath, "interpreter"); 
  const pythonInterpreter = path.join(interpreterDir, "interpreter.py");

  let command: string | undefined;
  let args: string[] = [];

  // 1️⃣ Priority 1: Try OS-specific compiled binary first.
  let binaryPath: string | undefined;
  
  if (platform === "win32") {
    binaryPath = path.join(interpreterDir, "interpreter-win.exe");
  } else if (platform === "darwin") { // ✅ macOS support
    binaryPath = path.join(interpreterDir, "interpreter-macos");
  } else if (platform === "linux") {
    binaryPath = path.join(interpreterDir, "interpreter-linux");
  }
  
  // Check if the correct binary exists.
  if (binaryPath && fs.existsSync(binaryPath)) {
    command = binaryPath;
    args = [filePath];
    
    // Crucial: Ensure the executable bit is set on Linux/macOS
    if (platform !== "win32") {
      try {
        fs.chmodSync(command, 0o755); 
      } catch (e) {
        console.error('Failed to set executable permission:', e);
      }
    }
  }

  // 2️⃣ Priority 2: Fallback to Python script execution.
  if (!command) {
    // Check if the script exists
    if (!fs.existsSync(pythonInterpreter)) {
      vscode.window.showErrorMessage(
        "Could not find any EAP interpreter: OS-specific executable missing AND 'interpreter.py' not found."
      );
      return;
    }
    
    // Check for system Python installation
    if (commandExists("python3")) {
      command = "python3";
      args = [pythonInterpreter, filePath];
    } else if (commandExists("python")) {
      command = "python";
      args = [pythonInterpreter, filePath];
    } else {
      vscode.window.showErrorMessage(
        "Found 'interpreter.py' but could not find a globally accessible 'python' or 'python3' command."
      );
      return;
    }
  }

  // The command variable is now guaranteed to be set if we reached this point.
  
  const terminal = vscode.window.createTerminal("EAP Runner");
  terminal.show();

  // Create the argument string, ensuring all arguments are quoted
  const argString = args.map(a => `"${a}"`).join(" ");

  let commandText: string;

  if (platform === "win32") {
      // Command path is NOT quoted, and use the '&' invocation operator.
      // E.g., & C:\path\to\interpreter-win.exe "C:\path\to\file with spaces.eap"
      commandText = `& ${command} ${argString}`; 
  } else {
      // For Linux/macOS, quote the command and arguments (standard Unix behavior).
      commandText = `"${command}" ${argString}`;
  }
  
  terminal.sendText(commandText);
}
