#!/usr/bin/env node
/**
 * SMEM Reader - Text Backup File Parser
 * Reads and displays SMEM/SMS backup files (XML, JSON, or structured text)
 * 
 * Usage: smem <file> [options]
 *   -f, --format <type>   Force format: xml, json, text (auto-detect if omitted)
 *   -s, --search <term>   Search within messages
 *   -o, --output <file>   Export to file (json/csv)
 *   --stats               Show statistics only
 *   -h, --help            Show help
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// ANSI colors
const c = {
    reset: '\x1b[0m',
    bold: '\x1b[1m',
    dim: '\x1b[2m',
    cyan: '\x1b[36m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    magenta: '\x1b[35m',
    red: '\x1b[31m',
    blue: '\x1b[34m',
    gray: '\x1b[90m'
};

// Simple XML parser for SMS backup formats
function parseXML(content) {
    const messages = [];

    // Common SMS backup XML patterns
    const smsRegex = /<sms\s+([^>]+)\/?>|<message\s+([^>]+)\/?>/gi;
    const attrRegex = /(\w+)="([^"]*)"/g;

    let match;
    while ((match = smsRegex.exec(content)) !== null) {
        const attrString = match[1] || match[2];
        const msg = {};

        let attrMatch;
        while ((attrMatch = attrRegex.exec(attrString)) !== null) {
            msg[attrMatch[1].toLowerCase()] = attrMatch[2];
        }

        // Normalize fields
        const normalized = {
            address: msg.address || msg.number || msg.phone || 'Unknown',
            body: msg.body || msg.text || msg.message || '',
            date: msg.date || msg.time || msg.timestamp || '',
            type: msg.type || msg.direction || '1', // 1=received, 2=sent
            contact: msg.contact_name || msg.name || msg.contact || null
        };

        // Decode HTML entities
        normalized.body = normalized.body
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&amp;/g, '&')
            .replace(/&quot;/g, '"')
            .replace(/&#10;/g, '\n')
            .replace(/&#(\d+);/g, (m, code) => String.fromCharCode(code));

        if (normalized.body || normalized.address !== 'Unknown') {
            messages.push(normalized);
        }
    }

    return messages;
}

// JSON parser for various backup formats
function parseJSON(content) {
    try {
        const data = JSON.parse(content);
        const messages = [];

        // Handle array of messages directly
        const arr = Array.isArray(data) ? data : (data.messages || data.sms || data.data || []);

        for (const item of arr) {
            messages.push({
                address: item.address || item.number || item.phone || item.sender || 'Unknown',
                body: item.body || item.text || item.message || item.content || '',
                date: item.date || item.time || item.timestamp || item.date_sent || '',
                type: item.type || item.direction || (item.sent ? '2' : '1'),
                contact: item.contact_name || item.name || item.contact || null
            });
        }

        return messages;
    } catch (e) {
        throw new Error(`JSON parse error: ${e.message}`);
    }
}

// Generic text parser (line-based)
function parseText(content) {
    const messages = [];
    const lines = content.split('\n');

    let currentMsg = null;

    for (const line of lines) {
        // Try to detect message headers (common patterns)
        const headerMatch = line.match(/^(?:From|To|Sender|Number):\s*(.+)/i) ||
            line.match(/^\[?(\+?\d[\d\s\-()]+)\]?\s*[-:]/);

        if (headerMatch) {
            if (currentMsg) messages.push(currentMsg);
            currentMsg = {
                address: headerMatch[1].trim(),
                body: '',
                date: '',
                type: '1',
                contact: null
            };
        } else if (currentMsg && line.trim()) {
            // Check for date line
            const dateMatch = line.match(/^(?:Date|Time|Sent|Received):\s*(.+)/i);
            if (dateMatch) {
                currentMsg.date = dateMatch[1].trim();
            } else {
                currentMsg.body += (currentMsg.body ? '\n' : '') + line;
            }
        }
    }

    if (currentMsg) messages.push(currentMsg);
    return messages;
}

// Detect format from content
function detectFormat(content) {
    const trimmed = content.trim();
    if (trimmed.startsWith('<?xml') || trimmed.startsWith('<')) return 'xml';
    if (trimmed.startsWith('{') || trimmed.startsWith('[')) return 'json';
    return 'text';
}

// Format date for display
function formatDate(dateStr) {
    if (!dateStr) return '';

    // Handle millisecond timestamps
    const ts = parseInt(dateStr);
    if (!isNaN(ts) && ts > 1000000000000) {
        return new Date(ts).toLocaleString();
    } else if (!isNaN(ts) && ts > 1000000000) {
        return new Date(ts * 1000).toLocaleString();
    }

    return dateStr;
}

// Display messages
function displayMessages(messages, searchTerm = null) {
    const filtered = searchTerm
        ? messages.filter(m =>
            m.body.toLowerCase().includes(searchTerm.toLowerCase()) ||
            m.address.toLowerCase().includes(searchTerm.toLowerCase()))
        : messages;

    console.log(`\n${c.cyan}${c.bold}═══ SMEM Backup Reader ═══${c.reset}`);
    console.log(`${c.dim}Found ${filtered.length}${searchTerm ? ' matching' : ''} messages${c.reset}\n`);

    for (let i = 0; i < filtered.length; i++) {
        const m = filtered[i];
        const direction = m.type === '2' || m.type === 'sent' ? '→' : '←';
        const dirColor = direction === '→' ? c.green : c.blue;
        const contact = m.contact ? `${m.contact} ` : '';

        console.log(`${c.gray}[${i + 1}]${c.reset} ${dirColor}${direction}${c.reset} ${c.bold}${contact}${c.yellow}${m.address}${c.reset}`);

        if (m.date) {
            console.log(`    ${c.dim}${formatDate(m.date)}${c.reset}`);
        }

        if (m.body) {
            const lines = m.body.split('\n');
            for (const line of lines) {
                console.log(`    ${line}`);
            }
        }
        console.log();
    }

    return filtered;
}

// Show statistics
function showStats(messages) {
    const contacts = {};
    let sent = 0, received = 0;

    for (const m of messages) {
        const addr = m.contact || m.address;
        contacts[addr] = (contacts[addr] || 0) + 1;
        if (m.type === '2' || m.type === 'sent') sent++;
        else received++;
    }

    console.log(`\n${c.cyan}${c.bold}═══ SMEM Statistics ═══${c.reset}\n`);
    console.log(`${c.bold}Total Messages:${c.reset} ${messages.length}`);
    console.log(`${c.green}Sent:${c.reset} ${sent}  ${c.blue}Received:${c.reset} ${received}`);
    console.log(`${c.bold}Unique Contacts:${c.reset} ${Object.keys(contacts).length}\n`);

    console.log(`${c.bold}Top Contacts:${c.reset}`);
    const sorted = Object.entries(contacts).sort((a, b) => b[1] - a[1]).slice(0, 10);
    for (const [name, count] of sorted) {
        console.log(`  ${c.yellow}${name}${c.reset}: ${count} messages`);
    }
    console.log();
}

// Export to file
function exportMessages(messages, outputPath) {
    const ext = path.extname(outputPath).toLowerCase();

    if (ext === '.csv') {
        const header = 'Address,Contact,Date,Type,Body';
        const rows = messages.map(m =>
            `"${m.address}","${m.contact || ''}","${m.date}","${m.type}","${m.body.replace(/"/g, '""')}"`
        );
        fs.writeFileSync(outputPath, header + '\n' + rows.join('\n'));
    } else {
        fs.writeFileSync(outputPath, JSON.stringify(messages, null, 2));
    }

    console.log(`${c.green}Exported ${messages.length} messages to ${outputPath}${c.reset}`);
}

// Interactive mode
async function interactiveMode(messages) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        prompt: `${c.magenta}smem>${c.reset} `
    });

    console.log(`\n${c.dim}Commands: search <term>, stats, list [n], export <file>, quit${c.reset}\n`);
    rl.prompt();

    rl.on('line', (line) => {
        const [cmd, ...args] = line.trim().split(' ');
        const arg = args.join(' ');

        switch (cmd.toLowerCase()) {
            case 'search':
            case 's':
                displayMessages(messages, arg);
                break;
            case 'stats':
                showStats(messages);
                break;
            case 'list':
            case 'l':
                const n = parseInt(arg) || 20;
                displayMessages(messages.slice(0, n));
                break;
            case 'export':
            case 'e':
                if (arg) exportMessages(messages, arg);
                else console.log(`${c.red}Usage: export <filename.json|csv>${c.reset}`);
                break;
            case 'quit':
            case 'exit':
            case 'q':
                process.exit(0);
            default:
                if (cmd) console.log(`${c.dim}Unknown command. Try: search, stats, list, export, quit${c.reset}`);
        }

        rl.prompt();
    });
}

// Main
async function main() {
    const args = process.argv.slice(2);
    let filePath = null;
    let format = null;
    let searchTerm = null;
    let outputPath = null;
    let statsOnly = false;

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        switch (arg) {
            case '-f':
            case '--format':
                format = args[++i];
                break;
            case '-s':
            case '--search':
                searchTerm = args[++i];
                break;
            case '-o':
            case '--output':
                outputPath = args[++i];
                break;
            case '--stats':
                statsOnly = true;
                break;
            case '-h':
            case '--help':
                console.log(`
${c.bold}SMEM Reader${c.reset} - Parse SMS/Text Backup Files

${c.cyan}Usage:${c.reset}
  smem <file>                    Read and display backup file
  smem <file> -s "term"          Search messages
  smem <file> --stats            Show statistics
  smem <file> -o out.json        Export to JSON/CSV

${c.cyan}Options:${c.reset}
  -f, --format <type>   Force format: xml, json, text
  -s, --search <term>   Search within messages
  -o, --output <file>   Export to file (.json or .csv)
  --stats               Show statistics only
  -h, --help            Show this help

${c.cyan}Supported Formats:${c.reset}
  • XML (SMS Backup & Restore, etc.)
  • JSON (various backup apps)
  • Structured text files
`);
                process.exit(0);
            default:
                if (!arg.startsWith('-')) filePath = arg;
        }
    }

    if (!filePath) {
        console.error(`${c.red}Error: No file specified. Use: smem <file>${c.reset}`);
        process.exit(1);
    }

    if (!fs.existsSync(filePath)) {
        console.error(`${c.red}Error: File not found: ${filePath}${c.reset}`);
        process.exit(1);
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    format = format || detectFormat(content);

    let messages;
    try {
        switch (format) {
            case 'xml':
                messages = parseXML(content);
                break;
            case 'json':
                messages = parseJSON(content);
                break;
            default:
                messages = parseText(content);
        }
    } catch (e) {
        console.error(`${c.red}Parse error: ${e.message}${c.reset}`);
        process.exit(1);
    }

    console.log(`${c.dim}Loaded ${messages.length} messages from ${path.basename(filePath)} (${format})${c.reset}`);

    if (outputPath) {
        exportMessages(messages, outputPath);
    } else if (statsOnly) {
        showStats(messages);
    } else if (searchTerm) {
        displayMessages(messages, searchTerm);
    } else {
        // Interactive mode if lots of messages, otherwise display all
        if (messages.length > 50) {
            displayMessages(messages.slice(0, 20));
            console.log(`${c.dim}Showing first 20 of ${messages.length}. Entering interactive mode...${c.reset}`);
            await interactiveMode(messages);
        } else {
            displayMessages(messages);
        }
    }
}

main().catch(e => {
    console.error(`${c.red}Error: ${e.message}${c.reset}`);
    process.exit(1);
});
