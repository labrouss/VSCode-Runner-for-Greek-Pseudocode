import * as vscode from "vscode";
import { registerAutocomplete } from "./autocomplete";
import { runEapProgram } from "./runEap";

export function activate(context: vscode.ExtensionContext) {
  registerAutocomplete(context);

  context.subscriptions.push(
    vscode.commands.registerCommand("eap.run", () =>
      runEapProgram(context)
    )
  );
}

export function deactivate() {}

