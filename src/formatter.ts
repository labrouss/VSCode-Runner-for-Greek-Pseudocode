import * as vscode from "vscode";

// Keywords that increase indentation
const INDENT_INCREASE_KEYWORDS = [
    'ΑΛΓΟΡΙΘΜΟΣ', 'ΑΡΧΗ', 'ΤΟΤΕ', 'ΑΛΛΙΩΣ', 'ΕΠΑΝΑΛΑΒΕ', 
    'ΕΠΑΝΑΛΗΨΗ', 'ΔΙΑΔΙΚΑΣΙΑ', 'ΣΥΝΑΡΤΗΣΗ', 'ΕΝΟΣΩ', 'ΓΙΑ'
];

// Keywords that decrease indentation (closing keywords)
const INDENT_DECREASE_KEYWORDS = [
    'ΤΕΛΟΣ', 'ΕΑΝ-ΤΕΛΟΣ', 'ΓΙΑ-ΤΕΛΟΣ', 'ΕΝΟΣΩ-ΤΕΛΟΣ', 
    'ΤΕΛΟΣ-ΔΙΑΔΙΚΑΣΙΑΣ', 'ΤΕΛΟΣ-ΣΥΝΑΡΤΗΣΗΣ', 'END', 'ΑΛΛΙΩΣ'
];

// Keywords that are both (decrease then increase)
const INDENT_BOTH_KEYWORDS = ['ΑΛΛΙΩΣ'];

export function registerFormatter(context: vscode.ExtensionContext) {
    const formatter = vscode.languages.registerDocumentFormattingEditProvider('eap', {
        provideDocumentFormattingEdits(document: vscode.TextDocument): vscode.TextEdit[] {
            const edits: vscode.TextEdit[] = [];
            let indentLevel = 0;
            const tabSize = vscode.workspace.getConfiguration('editor').get<number>('tabSize') || 4;
            const insertSpaces = vscode.workspace.getConfiguration('editor').get<boolean>('insertSpaces') ?? true;
            
            for (let i = 0; i < document.lineCount; i++) {
                const line = document.lineAt(i);
                const trimmedText = line.text.trim();
                
                // Skip empty lines
                if (trimmedText.length === 0) {
                    continue;
                }
                
                // Check if this line should decrease indent before formatting
                const shouldDecreaseBeforeFormat = INDENT_DECREASE_KEYWORDS.some(keyword => 
                    trimmedText.startsWith(keyword)
                );
                
                // Apply decrease before this line
                if (shouldDecreaseBeforeFormat && indentLevel > 0) {
                    indentLevel--;
                }
                
                // Calculate the correct indentation
                const correctIndent = insertSpaces 
                    ? ' '.repeat(indentLevel * tabSize)
                    : '\t'.repeat(indentLevel);
                
                // Get current indentation
                const currentIndent = line.text.substring(0, line.firstNonWhitespaceCharacterIndex);
                
                // If indentation is incorrect, create an edit
                if (currentIndent !== correctIndent) {
                    const range = new vscode.Range(
                        new vscode.Position(i, 0),
                        new vscode.Position(i, line.firstNonWhitespaceCharacterIndex)
                    );
                    edits.push(vscode.TextEdit.replace(range, correctIndent));
                }
                
                // Check if this line should increase indent for next line
                const shouldIncreaseAfterFormat = INDENT_INCREASE_KEYWORDS.some(keyword => 
                    trimmedText.startsWith(keyword)
                );
                
                if (shouldIncreaseAfterFormat) {
                    indentLevel++;
                }
                
                // Handle ΑΛΛΙΩΣ (decrease then increase)
                if (INDENT_BOTH_KEYWORDS.some(keyword => trimmedText.startsWith(keyword)) 
                    && !shouldDecreaseBeforeFormat) {
                    indentLevel++;
                }
            }
            
            return edits;
        }
    });
    
    context.subscriptions.push(formatter);
}

export function registerRangeFormatter(context: vscode.ExtensionContext) {
    const rangeFormatter = vscode.languages.registerDocumentRangeFormattingEditProvider('eap', {
        provideDocumentRangeFormattingEdits(
            document: vscode.TextDocument,
            range: vscode.Range
        ): vscode.TextEdit[] {
            const edits: vscode.TextEdit[] = [];
            const tabSize = vscode.workspace.getConfiguration('editor').get<number>('tabSize') || 4;
            const insertSpaces = vscode.workspace.getConfiguration('editor').get<boolean>('insertSpaces') ?? true;
            
            // Calculate initial indent level by scanning from start of document
            let indentLevel = 0;
            for (let i = 0; i < range.start.line; i++) {
                const line = document.lineAt(i);
                const trimmedText = line.text.trim();
                
                const decreases = INDENT_DECREASE_KEYWORDS.some(kw => trimmedText.startsWith(kw));
                const increases = INDENT_INCREASE_KEYWORDS.some(kw => trimmedText.startsWith(kw));
                
                if (decreases && indentLevel > 0) {
                    indentLevel--;
                }
                if (increases) {
                    indentLevel++;
                }
            }
            
            // Format the selected range
            for (let i = range.start.line; i <= range.end.line; i++) {
                const line = document.lineAt(i);
                const trimmedText = line.text.trim();
                
                if (trimmedText.length === 0) {
                    continue;
                }
                
                const shouldDecreaseBeforeFormat = INDENT_DECREASE_KEYWORDS.some(keyword => 
                    trimmedText.startsWith(keyword)
                );
                
                if (shouldDecreaseBeforeFormat && indentLevel > 0) {
                    indentLevel--;
                }
                
                const correctIndent = insertSpaces 
                    ? ' '.repeat(indentLevel * tabSize)
                    : '\t'.repeat(indentLevel);
                
                const currentIndent = line.text.substring(0, line.firstNonWhitespaceCharacterIndex);
                
                if (currentIndent !== correctIndent) {
                    const editRange = new vscode.Range(
                        new vscode.Position(i, 0),
                        new vscode.Position(i, line.firstNonWhitespaceCharacterIndex)
                    );
                    edits.push(vscode.TextEdit.replace(editRange, correctIndent));
                }
                
                const shouldIncreaseAfterFormat = INDENT_INCREASE_KEYWORDS.some(keyword => 
                    trimmedText.startsWith(keyword)
                );
                
                if (shouldIncreaseAfterFormat) {
                    indentLevel++;
                }
                
                if (INDENT_BOTH_KEYWORDS.some(keyword => trimmedText.startsWith(keyword)) 
                    && !shouldDecreaseBeforeFormat) {
                    indentLevel++;
                }
            }
            
            return edits;
        }
    });
    
    context.subscriptions.push(rangeFormatter);
}
