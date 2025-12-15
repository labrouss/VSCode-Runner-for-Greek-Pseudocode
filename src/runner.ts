import * as vscode from 'vscode';
import * as path from 'path';
import { spawn } from 'child_process';

export class PseudocodeRunner {
    private outputChannel: vscode.OutputChannel;
    private terminal: vscode.Terminal | undefined;

    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('EAP Pseudocode');
    }

    async runFile(document: vscode.TextDocument, debug: boolean = false) {
        // Save document if modified
        if (document.isDirty) {
            await document.save();
        }

        const filePath = document.uri.fsPath;
        const config = vscode.workspace.getConfiguration('pseudocode');
        const pythonPath = config.get<string>('pythonPath', 'python3');

        // Get the interpreter path
        const extensionPath = vscode.extensions.getExtension('your-publisher.pseudocode')?.extensionPath;
        if (!extensionPath) {
            vscode.window.showErrorMessage('Extension path not found');
            return;
        }

        const interpreterPath = path.join(extensionPath, 'interpreters', 'interpreter.py');

        // Check if file needs input (contains ΔΙΑΒΑΣΕ)
        const text = document.getText();
        const needsInput = /ΔΙΑΒΑΣΕ|READ/i.test(text);

        if (needsInput) {
            // Use integrated terminal for interactive input
            this.runInTerminal(pythonPath, interpreterPath, filePath, debug);
        } else {
            // Use output channel for non-interactive execution
            this.runInOutputChannel(pythonPath, interpreterPath, filePath, debug);
        }
    }

    private runInTerminal(pythonPath: string, interpreterPath: string, filePath: string, debug: boolean) {
        // Close existing terminal if any
        if (this.terminal) {
            this.terminal.dispose();
        }

        // Create new terminal
        this.terminal = vscode.window.createTerminal({
            name: 'EAP Pseudocode',
            iconPath: new vscode.ThemeIcon('play')
        });

        this.terminal.show();

        // Build command
        const args = [interpreterPath, filePath];
        if (debug) {
            args.push('--debug');
        }

        const command = `${pythonPath} ${args.map(arg => `"${arg}"`).join(' ')}`;
        this.terminal.sendText(command);
    }

    private runInOutputChannel(pythonPath: string, interpreterPath: string, filePath: string, debug: boolean) {
        this.outputChannel.clear();
        this.outputChannel.show(true);

        const args = [interpreterPath, filePath];
        if (debug) {
            args.push('--debug');
        }

        this.outputChannel.appendLine(`Running: ${pythonPath} ${args.join(' ')}`);
        this.outputChannel.appendLine('─'.repeat(80));

        const process = spawn(pythonPath, args, {
            cwd: path.dirname(filePath)
        });

        process.stdout.on('data', (data) => {
            this.outputChannel.append(data.toString());
        });

        process.stderr.on('data', (data) => {
            this.outputChannel.append(data.toString());
        });

        process.on('close', (code) => {
            this.outputChannel.appendLine('');
            this.outputChannel.appendLine('─'.repeat(80));
            if (code === 0) {
                this.outputChannel.appendLine('✓ Execution completed successfully');
            } else {
                this.outputChannel.appendLine(`✗ Execution failed with code ${code}`);
            }
        });

        process.on('error', (err) => {
            vscode.window.showErrorMessage(`Failed to run Python: ${err.message}`);
            this.outputChannel.appendLine(`Error: ${err.message}`);
            this.outputChannel.appendLine('Make sure Python 3 is installed and configured in settings');
        });
    }

    dispose() {
        this.outputChannel.dispose();
        if (this.terminal) {
            this.terminal.dispose();
        }
    }
}
