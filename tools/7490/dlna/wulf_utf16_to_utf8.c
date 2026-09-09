static __inline__ unsigned read_le16(const unsigned char *p)
{
    unsigned v;
    __asm__("lhu %0,0(%1)\n\twsbh %0,%0" : "=r"(v) : "r"(p));
    return v;
}

void wulf_utf16_to_utf8(char *out, const unsigned char *in, unsigned outlen)
{
    if (!outlen) return;
    while (outlen > 1) {
        unsigned v = read_le16(in), cp = v, n, shift, need;
        if (!v) break;
        in += 2;
        if ((v & 0xfc00) == 0xd800) {
            unsigned lo = read_le16(in);
            if ((lo & 0xfc00) == 0xdc00) {
                cp = 0x10000 + ((v - 0xd800) << 10) + (lo - 0xdc00);
                in += 2;
            } else cp = 0xfffd;
        } else if ((v & 0xfc00) == 0xdc00) cp = 0xfffd;
        if (cp < 0x80) n = 1;
        else if (cp < 0x800) n = 2;
        else if (cp < 0x10000) n = 3;
        else n = 4;
        need = n;
        if (outlen <= need) break;
        if (n == 1) *out++ = (char)cp;
        else {
            shift = (n - 1) * 6;
            *out++ = (char)((0x0f00 >> n) | (cp >> shift));
            while (--n) {
                shift -= 6;
                *out++ = (char)(0x80 | ((cp >> shift) & 0x3f));
            }
        }
        outlen -= need;
    }
    *out = 0;
}
