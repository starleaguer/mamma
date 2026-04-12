const fs = require('fs');
const path = require('path');

const envPath = path.resolve(__dirname, '.env');
const configPath = path.resolve(__dirname, 'config.js');

const readEnvFile = () => {
  if (!fs.existsSync(envPath)) return {};
  const envContent = fs.readFileSync(envPath, 'utf8');
  return envContent.split(/\r?\n/).reduce((acc, line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) return acc;
    const index = trimmed.indexOf('=');
    if (index === -1) return acc;
    const key = trimmed.slice(0, index).trim();
    let value = trimmed.slice(index + 1).trim();
    if (value.startsWith('"') && value.endsWith('"')) {
      value = value.slice(1, -1);
    }
    acc[key] = value;
    return acc;
  }, {});
};

const envFromFile = readEnvFile();
const env = {
  SUPABASE_URL: process.env.SUPABASE_URL || envFromFile.SUPABASE_URL,
  SUPABASE_KEY: process.env.SUPABASE_KEY || envFromFile.SUPABASE_KEY,
  BASE_URL: process.env.BASE_URL || envFromFile.BASE_URL,
};

const requiredKeys = ['SUPABASE_URL', 'SUPABASE_KEY', 'BASE_URL'];
const missingKeys = requiredKeys.filter((key) => !env[key]);

if (missingKeys.length > 0) {
  console.error('Missing required config values:', missingKeys.join(', '));
  process.exit(1);
}

const configContent = `/*
  Generated from environment variables. Do not commit sensitive values.
*/
window.CONFIG = ${JSON.stringify(env, null, 2)};
`;

fs.writeFileSync(configPath, configContent, 'utf8');
console.log('config.js generated from environment variables');
