/**
 * MOL Language Extension — LSP Client
 *
 * Connects to the MOL Language Server (Python) for:
 * - Autocomplete (99 stdlib functions + keywords + user symbols)
 * - Hover documentation
 * - Real-time diagnostics (parse errors)
 * - Signature help (parameter hints)
 * - Go-to-definition (user functions/variables)
 * - Document symbols (outline view)
 */

import * as path from "path";
import * as vscode from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;

export function activate(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("mol");
  const lspEnabled = config.get<boolean>("lsp.enabled", true);

  if (!lspEnabled) {
    console.log("MOL LSP disabled by configuration");
    return;
  }

  startLanguageServer(context);

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand("mol.restartServer", async () => {
      if (client) {
        await client.stop();
        client = undefined;
      }
      startLanguageServer(context);
      vscode.window.showInformationMessage("MOL Language Server restarted.");
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("mol.runFile", () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || editor.document.languageId !== "mol") {
        vscode.window.showWarningMessage("Open a .mol file to run it.");
        return;
      }

      const filePath = editor.document.fileName;
      const terminal =
        vscode.window.terminals.find((t) => t.name === "MOL") ||
        vscode.window.createTerminal("MOL");
      terminal.show();
      terminal.sendText(`mol run "${filePath}"`);
    })
  );

  // Status bar
  const statusBar = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    100
  );
  statusBar.text = "$(symbol-misc) MOL";
  statusBar.tooltip = "MOL Language Server";
  statusBar.command = "mol.restartServer";
  statusBar.show();
  context.subscriptions.push(statusBar);
}

function startLanguageServer(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("mol");
  const pythonPath = config.get<string>("lsp.pythonPath", "python3");

  // The server is a Python module: mol.lsp_server
  const serverOptions: ServerOptions = {
    command: pythonPath,
    args: ["-m", "mol.lsp_server"],
    transport: TransportKind.stdio,
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: "file", language: "mol" }],
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher("**/*.mol"),
    },
    outputChannelName: "MOL Language Server",
  };

  client = new LanguageClient(
    "mol-language-server",
    "MOL Language Server",
    serverOptions,
    clientOptions
  );

  client.start().then(
    () => {
      console.log("MOL Language Server started successfully");
    },
    (err) => {
      console.error("Failed to start MOL Language Server:", err);
      vscode.window.showErrorMessage(
        `MOL Language Server failed to start. Make sure mol-lang is installed: pip install mol-lang\n\nError: ${err.message}`
      );
    }
  );

  context.subscriptions.push({
    dispose: () => {
      if (client) {
        client.stop();
      }
    },
  });
}

export function deactivate(): Thenable<void> | undefined {
  if (!client) {
    return undefined;
  }
  return client.stop();
}
