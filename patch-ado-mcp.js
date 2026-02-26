#!/usr/bin/env node
// =============================================================================
// Patch @azure-devops/mcp — add corporate proxy + TLS bypass support
// =============================================================================
// Problem:
//   In src/index.ts, getAzureDevOpsClient() passes `undefined` as the third
//   argument (IRequestOptions) to new WebApi(orgUrl, authHandler, undefined, …).
//   typed-rest-client reads proxy settings from IRequestOptions.proxy and TLS
//   settings from IRequestOptions.ignoreSslError, so without this argument
//   the MCP server cannot reach Azure DevOps through a corporate proxy.
//
// Fix:
//   Replace `undefined` with a runtime expression that reads:
//     HTTPS_PROXY / HTTP_PROXY / NO_PROXY     → proxy routing
//     ADO_MCP_TLS_SKIP_VERIFY=true            → disable TLS cert verification
//
// Usage (Dockerfile):
//   COPY patch-ado-mcp.js /tmp/patch-ado-mcp.js
//   RUN node /tmp/patch-ado-mcp.js && rm /tmp/patch-ado-mcp.js
//
// Reference:
//   https://github.com/microsoft/azure-devops-mcp/blob/main/src/index.ts
//   typed-rest-client IRequestOptions:
//     proxy: { proxyUrl, proxyBypassHosts? }
//     ignoreSslError: boolean
// =============================================================================

'use strict';

const fs   = require('fs');
const path = require('path');

// ── Locate the compiled main file ───────────────────────────────────────────

const pkgDir  = path.dirname(require.resolve('@azure-devops/mcp/package.json'));
const pkgJson = JSON.parse(fs.readFileSync(path.join(pkgDir, 'package.json'), 'utf8'));

// Resolve main: package.json "main", then "exports['.'].require", then fallback
const mainRel =
  pkgJson.main ||
  pkgJson.exports?.['./']?.require ||
  pkgJson.exports?.['.']?.require  ||
  pkgJson.exports?.['.']           ||
  'dist/index.js';

const mainFile = path.join(pkgDir, typeof mainRel === 'string' ? mainRel : 'dist/index.js');

console.log('[patch-ado-mcp] Target file:', mainFile);

let src = fs.readFileSync(mainFile, 'utf8');

// ── Find the WebApi instantiation that needs patching ───────────────────────
//
// TypeScript:  new WebApi(orgUrl, authHandler, undefined, { … })
// Compiled JS: new WebApi(orgUrl, authHandler, undefined, {
//           or new azure_devops_node_api_1.WebApi(orgUrl, authHandler, undefined, {
//
// We match the three positional args (orgUrl, authHandler, undefined) which is
// the unique signature — no other WebApi call has this exact pattern.

const PATTERN = /new\s+(?:[\w$]+\.)?WebApi\(\s*orgUrl\s*,\s*authHandler\s*,\s*undefined\s*,\s*\{/;

if (!PATTERN.test(src)) {
  console.error('[patch-ado-mcp] ERROR: expected pattern not found in', mainFile);
  console.error('[patch-ado-mcp] The package may have changed — review the patch.');
  process.exit(1);
}

// ── Build the replacement IRequestOptions expression ────────────────────────
//
// Evaluated at runtime (each time the MCP server starts), not at build time.
//
// typed-rest-client IRequestOptions shape:
//   proxy?:         { proxyUrl: string; proxyBypassHosts?: string[] }
//   ignoreSslError?: boolean

const OPTIONS_EXPR = [
  '(function(){',
  '  var _opts={};',
  '  var _p=process.env.HTTPS_PROXY||process.env.https_proxy',
  '        ||process.env.HTTP_PROXY||process.env.http_proxy||"";',
  '  if(_p){',
  '    var _n=(process.env.NO_PROXY||process.env.no_proxy||"")',
  '          .split(",").map(function(s){return s.trim();}).filter(Boolean);',
  '    _opts.proxy={proxyUrl:_p,proxyBypassHosts:_n};',
  '  }',
  '  if(process.env.ADO_MCP_TLS_SKIP_VERIFY==="true"){',
  '    _opts.ignoreSslError=true;',
  '  }',
  '  return Object.keys(_opts).length?_opts:undefined;',
  '})()',
].join('');

src = src.replace(
  PATTERN,
  (match) => match.replace(/,\s*undefined\s*,\s*\{/, `, ${OPTIONS_EXPR}, {`)
);

// ── Write back ───────────────────────────────────────────────────────────────

fs.writeFileSync(mainFile, src, 'utf8');
console.log('[patch-ado-mcp] Patch applied successfully.');
console.log('[patch-ado-mcp] Runtime env vars:');
console.log('[patch-ado-mcp]   HTTPS_PROXY / HTTP_PROXY  — route through proxy');
console.log('[patch-ado-mcp]   NO_PROXY                  — bypass list');
console.log('[patch-ado-mcp]   ADO_MCP_TLS_SKIP_VERIFY=true — disable TLS cert check');
