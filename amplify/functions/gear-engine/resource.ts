import { defineFunction } from '@aws-amplify/backend';

export const gearEngine = defineFunction({
  name: 'gear-engine',
  entry: './handler.py' // Pointing directly to your Python file
});