import * as vscode from "vscode";

// Keywords that increase indentation for NEXT line
const INDENT_INCREASE_NEXT_LINE = [
    'ΤΟΤΕ', 'ΑΛΛΙΩΣ', 'ΕΠΑΝΑΛΑΒΕ'
];

// Keywords that decrease indentation (closing keywords)
const INDENT_DECREASE_KEYWORDS = [
    'ΕΑΝ-ΤΕΛΟΣ', 'ΓΙΑ-ΤΕΛΟΣ', 'ΕΝΟΣΩ-ΤΕΛΟΣ', 
    'ΤΕΛΟΣ-ΔΙΑΔΙΚΑΣΙΑΣ', 'ΤΕΛΟΣ-ΣΥΝΑΡΤΗΣΗΣ', 'ΑΛΛΙΩΣ', 'ΜΕΧΡΙ'
];

// Keywords that always go to column 0 (no indentation)
const ZERO_INDENT_KEYWORDS = ['ΤΕΛΟΣ', 'ΑΡΧΗ'];

// Keywords that have special handling (start of line with block)
const LOOP_WITH_BLOCK_KEYWORDS = [
    'ΓΙΑ', 'ΕΝΟΣΩ'
];

function analyzeLine(trimmedLine: string): { 
    hasIncreaseNextLine: boolean;
    hasDecrease: boolean;
    isLoopWithBlock: boolean;
    isZeroIndent: boolean;
} {
    const upperLine = trimmedLine.toUpperCase();
    
    // Check if it's ΤΕΛΟΣ (should always be at column 0)
    const isZeroIndent = ZERO_INDENT_KEYWORDS.some(kw => upperLine.startsWith(kw));
    
    // Check if it's a ΓΙΑ or ΕΝΟΣΩ line that contains ΕΠΑΝΑΛΑΒΕ
    const isLoopWithBlock = LOOP_WITH_BLOCK_KEYWORDS.some(kw => upperLine.startsWith(kw)) 
                            && upperLine.includes('ΕΠΑΝΑΛΑΒΕ');
    
    // ΕΠΑΝΑΛΑΒΕ on its own line (not part of ΓΙΑ/ΕΝΟΣΩ) increases next line
    const standaloneEpanalabe = upperLine.startsWith('ΕΠΑΝΑΛΑΒΕ') 
                                && !LOOP_WITH_BLOCK_KEYWORDS.some(kw => upperLine.includes(kw));
    
    return {
        hasIncreaseNextLine: INDENT_INCREASE_NEXT_LINE.some(kw => upperLine.startsWith(kw)) || standaloneEpanalabe,
        hasDecrease: INDENT_DECREASE_KEYWORDS.some(kw => upperLine.startsWith(kw)),
        isLoopWithBlock: isLoopWithBlock,
        isZeroIndent: isZeroIndent
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
                
                const analysis = analyzeLine(trimmedText);
                
                // ΤΕΛΟΣ always goes to column 0
                let effectiveIndentLevel = indentLevel;
                if (analysis.isZeroIndent) {
                    effectiveIndentLevel = 0;
                } else if (analysis.hasDecrease && indentLevel > 0) {
                    // Other closing keywords decrease indent normally
                    indentLevel--;
                    effectiveIndentLevel = indentLevel;
                }
                
                // Calculate the correct indentation for THIS line
                const correctIndent = insertSpaces 
                    ? ' '.repeat(effectiveIndentLevel * tabSize)
                    : '\t'.repeat(effectiveIndentLevel);
                
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
                if (analysis.isLoopWithBlock) {
                    // ΓΙΑ...ΕΠΑΝΑΛΑΒΕ or ΕΝΟΣΩ...ΕΠΑΝΑΛΑΒΕ increases indent
                    indentLevel++;
                } else if (analysis.hasIncreaseNextLine) {
                    // ΤΟΤΕ, ΑΛΛΙΩΣ, or standalone ΕΠΑΝΑΛΑΒΕ
                    indentLevel++;
                }
                
                // ΤΕΛΟΣ or ΑΡΧΗ resets indent to appropriate level
                if (analysis.isZeroIndent) {
                    if (trimmedText.toUpperCase().startsWith('ΑΡΧΗ')) {
                        // ΑΡΧΗ: next line should be indented once
                        indentLevel = 1;
                    } else {
                        // ΤΕΛΟΣ: reset to 0
                        indentLevel = 0;
                    }
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
                const analysis = analyzeLine(trimmedText);
                
                if (analysis.hasDecrease && indentLevel > 0) {
                    indentLevel--;
                }
                
                if (analysis.isLoopWithBlock) {
                    indentLevel++;
                } else if (analysis.hasIncreaseNextLine) {
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
                
                const analysis = analyzeLine(trimmedText);
                
                // ΤΕΛΟΣ always goes to column 0
                let effectiveIndentLevel = indentLevel;
                if (analysis.isZeroIndent) {
                    effectiveIndentLevel = 0;
                } else if (analysis.hasDecrease && indentLevel > 0) {
                    // Other closing keywords decrease indent normally
                    indentLevel--;
                    effectiveIndentLevel = indentLevel;
                }
                
                const correctIndent = insertSpaces 
                    ? ' '.repeat(effectiveIndentLevel * tabSize)
                    : '\t'.repeat(effectiveIndentLevel);
                
                const currentIndent = line.text.substring(0, line.firstNonWhitespaceCharacterIndex);
                
                if (currentIndent !== correctIndent) {
                    const editRange = new vscode.Range(
                        new vscode.Position(i, 0),
                        new vscode.Position(i, line.firstNonWhitespaceCharacterIndex)
                    );
                    edits.push(vscode.TextEdit.replace(editRange, correctIndent));
                }
                
                if (analysis.isLoopWithBlock) {
                    indentLevel++;
                } else if (analysis.hasIncreaseNextLine) {
                    indentLevel++;
                }
                
                // ΤΕΛΟΣ or ΑΡΧΗ resets indent to appropriate level
                if (analysis.isZeroIndent) {
                    if (trimmedText.toUpperCase().startsWith('ΑΡΧΗ')) {
                        // ΑΡΧΗ: next line should be indented once
                        indentLevel = 1;
                    } else {
                        // ΤΕΛΟΣ: reset to 0
                        indentLevel = 0;
                    }
                }
            }
            
            return edits;
        }
    });
    
    context.subscriptions.push(rangeFormatter);
}
