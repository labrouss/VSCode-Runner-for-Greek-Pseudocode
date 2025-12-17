import * as vscode from "vscode";
import { registerAutocomplete } from "./autocomplete";
import { runEapProgram } from "./runEap";

let myStatusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
    registerAutocomplete(context);

    // Register Run Command
    context.subscriptions.push(
        vscode.commands.registerCommand("eap.run", () => runEapProgram(context))
    );

    // --- Status Bar Setup ---
    myStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    context.subscriptions.push(myStatusBarItem);

    // Events to update status bar
    context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor(updateStatusBarItem));
    context.subscriptions.push(vscode.window.onDidChangeTextEditorSelection(updateStatusBarItem));

    updateStatusBarItem();
}

function updateStatusBarItem(): void {
    const editor = vscode.window.activeTextEditor;
    if (editor && editor.document.languageId === 'eap') {
        const text = editor.document.getText();
        // Look for ΑΛΓΟΡΙΘΜΟΣ followed by a name
        const match = text.match(/ΑΛΓΟΡΙΘΜΟΣ\s+([A-Za-zΑ-Ωα-ω0-9_]+)/);
        
        if (match && match[1]) {
            myStatusBarItem.text = `$(symbol-class) Alg: ${match[1]}`;
            myStatusBarItem.show();
        } else {
            myStatusBarItem.text = `$(symbol-class) No Name`;
            myStatusBarItem.show();
        }
    } else {
        myStatusBarItem.hide();
    }
}
