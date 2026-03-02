import app

with open('sample.txt','rb') as f:
    raw = f.read()
    print('raw repr:', repr(raw))
    # mimic extract endpoint decoding
    data = None
    for enc in ('utf-8', 'utf-16', 'latin-1'):
        try:
            candidate = raw.decode(enc)
            if enc == 'utf-8' and '\x00' in candidate:
                raise UnicodeDecodeError(enc, raw, 0, 1, 'nulls')
            data = candidate
            break
        except Exception:
            continue
    if data is None or data == '':
        data = raw.decode('utf-8', errors='ignore')
    decoded = data
    print('decoded repr lines:')
    for l in decoded.splitlines():
        print('  >', repr(l))
    print('parsed weights:', app.parse_weights_from_text(decoded))
