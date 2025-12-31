import * as vscode from "vscode";

// Keywords that increase indentation on the SAME line (block starts)
const INDENT_INCREASE_SAME_LINE = [
    'ΕΠΑΝΑΛΑΒΕ'  // ΓΙΑ/ΕΝΟΣΩ ... ΕΠΑΝΑΛΑΒΕ
];

// Keywords that increase indentation for NEXT line
const INDENT_INCREASE_NEXT_LINE = [
    'ΑΡΧΗ', 'ΤΟΤΕ', 'ΑΛΛΙΩΣ'
];

// Keywords that decrease indentation (closing keywords)
const INDENT_DECREASE_KEYWORDS = [
    'ΤΕΛΟΣ', 'ΕΑΝ-ΤΕΛΟΣ', 'ΓΙΑ-ΤΕΛΟΣ', 'ΕΝΟΣΩ-ΤΕΛΟΣ', 
    'ΤΕΛΟΣ-ΔΙΑΔΙΚΑΣΙΑΣ', 'ΤΕΛΟΣ-ΣΥΝΑΡΤΗΣΗΣ', 'ΑΛΛΙΩΣ'
];

function getLineKeywords(trimmedLine: string): { 
    hasIncreaseNextLine: boolean;
    hasIncreaseSameLine: boolean;
    hasDecrease: boolean;
} {
    const upperLine = trimmedLine.toUpperCase();
    
    return {
        hasIncreaseNextLine: INDENT_INCREASE_NEXT_LINE.some(kw => upperLine.startsWith(kw)),
        hasIncreaseSameLine: INDENT_INCREASE_SAME_LINE.some(kw => upperLine.includes(kw)),
        hasDecrease: INDENT_DECREASE_KEYWORDS.some(kw => upperLine.startsWith(kw))
    };
}

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
                
                const keywords = getLineKeywords(trimmedText);
                
                // Decrease indent BEFORE formatting this line if it's a closing keyword
                if (keywords.hasDecrease && indentLevel > 0) {
                    indentLevel--;
                }
                
                // Calculate the correct indentation for THIS line
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
                
                // Increase indent for NEXT line if needed
                // Priority: same-line keywords (ΕΠΑΝΑΛΑΒΕ) > next-line keywords (ΑΡΧΗ, ΤΟΤΕ)
                if (keywords.hasIncreaseSameLine) {
                    indentLevel++;
                } else if (keywords.hasIncreaseNextLine) {
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
            
            // Calculate initial indent level by scanning from start of document to range start
            let indentLevel = 0;
            for (let i = 0; i < range.start.line; i++) {
                const line = document.lineAt(i);
                const trimmedText = line.text.trim();
                const keywords = getLineKeywords(trimmedText);
                
                if (keywords.hasDecrease && indentLevel > 0) {
                    indentLevel--;
                }
                
                if (keywords.hasIncreaseSameLine) {
                    indentLevel++;
                } else if (keywords.hasIncreaseNextLine) {
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
                
                const keywords = getLineKeywords(trimmedText);
                
                if (keywords.hasDecrease && indentLevel > 0) {
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
                
                if (keywords.hasIncreaseSameLine) {
                    indentLevel++;
                } else if (keywords.hasIncreaseNextLine) {
                    indentLevel++;
                }
            }
            
            return edits;
        }
    });
    
    context.subscriptions.push(rangeFormatter);
}
