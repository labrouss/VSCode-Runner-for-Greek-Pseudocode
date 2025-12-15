import * as vscode from 'vscode';
import { PseudocodeRunner } from './runner';

let runner: PseudocodeRunner;

export function activate(context: vscode.ExtensionContext) {
    console.log('EAP Pseudocode extension is now active');

    // Create runner
    runner = new PseudocodeRunner();

    // Register run command
    let runCommand = vscode.commands.registerCommand('pseudocode.run', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        if (editor.document.languageId !== 'pseudocode') {
            vscode.window.showWarningMessage('This is not a pseudocode file');
            return;
        }

        await runner.runFile(editor.document, false);
    });

    // Register debug run command
    let runDebugCommand = vscode.commands.registerCommand('pseudocode.runDebug', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        if (editor.document.languageId !== 'pseudocode') {
            vscode.window.showWarningMessage('This is not a pseudocode file');
            return;
        }

        await runner.runFile(editor.document, true);
    });

    context.subscriptions.push(runCommand, runDebugCommand, runner);
}

export function deactivate() {
    if (runner) {
        runner.dispose();
    }
}
