// src/runner.ts

import * as vscode from 'vscode';
import * as path from 'path';

export function runPseudocode(extensionPath: string) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        return;
    }

    const config = vscode.workspace.getConfiguration('pseudocode');
    const filePath = editor.document.fileName;
    const dirName = path.dirname(filePath);

    // --- CRITICAL PATH LOGIC ---
    
    // 1. Define the default bundled interpreter path
    // Assuming your interpreter executable/script is named 'interpreter.exe' or 'main.py'
    const bundledInterpreterFilename = (process.platform === 'win32') 
        ? 'interpreter.exe' // e.g., for Windows executable
        : 'interpreter.sh'; // e.g., for Linux/Mac shell script or executable

    const defaultInterpreterPath = path.join(
        extensionPath, 
        'interpreter', 
        bundledInterpreterFilename
    );

    // 2. Allow user configuration to override the default (good practice)
    const configuredInterpreter = config.get<string>('interpreterPath');
    
    // Choose which path to use (configured or bundled)
    const interpreterPath = configuredInterpreter || defaultInterpreterPath;
    
    // 3. Ensure the file is saved before running
    editor.document.save();
    
    // --- TERMINAL EXECUTION (Best practice for I/O) ---
    
    // Command structure: "[path to interpreter]" "[path to code file]"
    // Quoting is ESSENTIAL for paths with spaces
    const command = `"${interpreterPath}" "${filePath}"\n`;

    const terminal = vscode.window.createTerminal({
        name: "Greek Pseudocode Runner",
        cwd: dirName // Start terminal in the same directory as the code file
    });

    terminal.show(true);
    terminal.sendText('cls || clear'); // Clear console (works on Windows/Linux/Mac)
    terminal.sendText(command);

    // Optional: Add a note to the terminal for the user
    terminal.sendText('\necho "--- Execution Finished ---"\n');
}
