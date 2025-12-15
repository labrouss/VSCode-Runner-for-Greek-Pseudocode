// src/extension.ts

import * as vscode from 'vscode';
import { runPseudocode } from './runner';

export function activate(context: vscode.ExtensionContext) {
    // Register the command and pass the extension's path to the runner function
    let disposable = vscode.commands.registerCommand('pseudocode.runInterpreter', () => {
        runPseudocode(context.extensionPath);
    });

    context.subscriptions.push(disposable);
}
