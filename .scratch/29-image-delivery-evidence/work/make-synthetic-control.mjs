import { deflateSync } from 'node:zlib';
import { mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';

const crcTable = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
const crc32 = (b) => { let c = 0xffffffff; for (const x of b) c = crcTable[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
const chunk = (type, data) => { const name = Buffer.from(type); const out = Buffer.alloc(12 + data.length); out.writeUInt32BE(data.length, 0); name.copy(out, 4); data.copy(out, 8); out.writeUInt32BE(crc32(Buffer.concat([name, data])), 8 + data.length); return out; };
const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(2, 0); ihdr.writeUInt32BE(2, 4); ihdr[8] = 8; ihdr[9] = 6;
const pixels = Buffer.from([0, 255, 0, 0, 255, 0, 255, 0, 255, 0, 0, 0, 255, 255, 255, 255, 255, 255]);
const png = Buffer.concat([Buffer.from('89504e470d0a1a0a', 'hex'), chunk('IHDR', ihdr), chunk('IDAT', deflateSync(pixels)), chunk('IEND', Buffer.alloc(0))]);
const out = '.scratch/29-image-delivery-evidence/evidence/control/synthetic-control.png';
await mkdir(path.dirname(out), { recursive: true, mode: 0o700 });
await writeFile(out, png, { mode: 0o600, flag: 'wx' });
console.log(JSON.stringify({ path: out, sha256: createHash('sha256').update(png).digest('hex'), byteLength: png.length }));
