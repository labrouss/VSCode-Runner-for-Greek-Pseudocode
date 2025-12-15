import * as vscode from "vscode";

const KEYWORDS = [
  "ΑΛΓΟΡΙΘΜΟΣ", "ΣΤΑΘΕΡΕΣ", "ΔΕΔΟΜΕΝΑ", "ΑΡΧΗ", "ΤΕΛΟΣ",
  "ΕΑΝ", "ΤΟΤΕ", "ΑΛΛΙΩΣ", "ΕΑΝ-ΤΕΛΟΣ",
  "ΓΙΑ", "ΕΩΣ", "ΒΗΜΑ", "ΕΠΑΝΑΛΑΒΕ", "ΓΙΑ-ΤΕΛΟΣ",
  "ΕΝΟΣΩ", "ΕΝΟΣΩ-ΤΕΛΟΣ", "ΜΕΧΡΙ",
  "ΤΥΠΩΣΕ", "ΔΙΑΒΑΣΕ"
];

export function registerAutocomplete(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.languages.registerCompletionItemProvider(
      "eap",
      {
        provideCompletionItems() {
          return KEYWORDS.map(k => {
            const item = new vscode.CompletionItem(k);
            item.kind = vscode.CompletionItemKind.Keyword;
            return item;
          });
        }
      },
      "" // trigger on letters
    )
  );
}

