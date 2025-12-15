const vscode = require("vscode");
const path = require("path");

let terminal;

function activate(context) {
  // ... (Notification and Manual Command logic is unchanged and omitted for brevity)

  // Register EAP runner
  const runEapCommand = vscode.commands.registerCommand(
    "pseudocode.runInterpreter",
    function () {
      const editor = vscode.window.activeTextEditor;

      if (!editor) {
        vscode.window.showErrorMessage("Δεν υπάρχει ενεργό αρχείο .eap για εκτέλεση.");
        return;
      }
      
      const filePath = editor.document.fileName;
      const fileDir = path.dirname(filePath);
      
      // --- 1. Determine OS and Interpreter Path ---
      const isWindows = process.platform === 'win32';
      
      // 1a. Get the path to the interpreter inside your extension folder
      // context.extensionPath is the base directory of your installed extension
      let bundledInterpreterPath = '';
      let interpreterExecutionCommand = '';
      
      if (isWindows) {
        // For Windows, use the bundled EXE
        bundledInterpreterPath = path.join(context.extensionPath, 'interpreter', 'interpreter.exe');
        // The command is just the executable path followed by the file path
        interpreterExecutionCommand = `"${bundledInterpreterPath}" "${filePath}"`;
      } else {
        // For Linux/macOS, use the Python script
        const pythonScriptPath = path.join(context.extensionPath, 'interpreter', 'interpreter.py');
        // The command requires the python executable + the script path + the file path
        // We assume 'python3' is available on Linux/Mac systems
        interpreterExecutionCommand = `python3 "${pythonScriptPath}" "${filePath}"`;
      }
      
      // --- 2. Create and Run in Terminal ---
      
      // Get configured path (allowing user to override bundled interpreter)
      const config = vscode.workspace.getConfiguration("pseudocode"); // Note: Assuming configuration title is 'pseudocode' not 'greekpseudocode'
      const configuredPath = config.get('interpreterPath');
      
      // Use configured path if available, otherwise use the bundled command
      const finalCommand = configuredPath 
                         ? `"${configuredPath}" "${filePath}"` 
                         : interpreterExecutionCommand;

      // Ensure the file is saved before running
      editor.document.save();
      
      // Create a new terminal for interaction (best for READ/ΔΙΑΒΑΣΕ)
      terminal = vscode.window.createTerminal({
          name: "Pseudocode Runner",
          cwd: fileDir, // Start in the file's directory
          // Note: We don't set shellPath here, we use the default system shell.
      });

      // Show terminal and send commands
      terminal.show();

      // Clear the terminal (cls for Windows, clear for Linux/Mac)
      const clearCommand = isWindows ? 'cls' : 'clear';
      terminal.sendText(clearCommand, true);

      // Execute the final command
      terminal.sendText(finalCommand + '\n', true);
      
      vscode.window.showInformationMessage(`Running Pseudocode: ${finalCommand}`);
    }
  );

  // ... (Your manual command and deactivate logic remain below)
}

// ... rest of the functions (getWebviewContent, deactivate)
