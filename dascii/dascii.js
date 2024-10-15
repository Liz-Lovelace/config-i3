#!/usr/bin/node

const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

main();

async function main() {
  let choice = await dmenuPrompt(['g: l r t b v h in any combination', 'i: check, cross'])

  let handler = {
    g: graphDrawer,
    i: getIcon,
  }[choice[0]]

  let result = handler(choice.slice(1))

  console.log(`${choice} -> ${result}`)

  await setClipboard(result)
}

function graphDrawer(str) {
  let chars = {
    '': ' ',
    't': '╵',
    'b': '╷',
    'l': '╴',
    'r': '╶',
    'bt': '│',
    'lr': '─',
    'tl': '┘',
    'tr': '└',
    'bl': '┐',
    'br': '┌',
    'btl': '┤',
    'tbr': '├',
    'tlr': '┴',
    'blr': '┬',
    'tblr': '┼'
  };

  chars = Object.fromEntries(Object.entries(chars).map(([k, v]) => [k.split('').sort().join(''), v]));

  let normalizedStr = str
    .replace(/v/g, 'tb')
    .replace(/h/g, 'lr');

  normalizedStr = [...new Set(normalizedStr)].sort().join('');

  return chars[normalizedStr] || '?';
}

function getIcon(str) {
  let icons = {
    check: '✔',
    cross: '✘',
  };
  console.log(icons)

  return icons[str] || '?';
}

async function dmenuPrompt(options) {
  let answer = await execCommand(`dmenu -b -nb "#000" -sb "#FFF" -nf "#FFF" -sf "#000"`, options.join(' |\n'));
  answer = answer.trim()
  if (answer.startsWith('| ')) {
    answer = answer.slice(2)
  }
  return answer
}

async function setClipboard(text) {
  await execCommand(`xclip -selection clipboard`, text)
}

async function execCommand(cmd, input = '') {
  const { stdout, stderr } = await execPromise(`echo -n "${input}" | ${cmd}`);
  return stdout;
}
