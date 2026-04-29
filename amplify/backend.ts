import { defineBackend } from '@aws-amplify/backend';
import { Stack } from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

// Manually define __dirname for ES Module scope
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const backend = defineBackend({
  // No auth or data needed for the MVP
});

// Create the custom stack
const customStack = backend.createStack('ScoutPackerStack');

const gearEngine = new lambda.Function(customStack, 'GearEngineFunction', {
  runtime: lambda.Runtime.PYTHON_3_12,
  handler: 'handler.handler',
  // This path.join now uses our manually defined __dirname
  code: lambda.Code.fromAsset(path.join(__dirname, 'functions', 'gear-engine')),
});

// Expose the Function URL and store the reference
const gearEngineUrl = gearEngine.addFunctionUrl({
  authType: lambda.FunctionUrlAuthType.NONE,
});

// 4. PUBLISH TO amplify_outputs.json
// This creates a custom entry in the JSON that your frontend can read
backend.addOutput({
  custom: {
    gearEngineUrl: gearEngineUrl.url,
  },
});