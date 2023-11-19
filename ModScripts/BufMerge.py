
dir = 'D:\\Naraka\\program\\Mods\\raw\\'
modName = 'zhizhujing'

if __name__ == '__main__':
    positionStride = 40
    texcoordStride = 8
    blendStride = 32

    pi = 0
    ti = 0
    bi = 0

    position = 'vb0'
    texcoord = 'vb1'
    blend = 'vb2'

    data = b''

    with open(f'{dir}{modName}_{position}.buf', 'rb') as position:
        with open(f'{dir}{modName}_{texcoord}.buf', 'rb') as texcoord:
            with open(f'{dir}{modName}_{blend}.buf', 'rb') as blend:
                while True:
                    position.seek(pi)
                    texcoord.seek(ti)
                    blend.seek(bi)

                    pData = position.read(positionStride)
                    tData = texcoord.read(texcoordStride)
                    bData = blend.read(blendStride)

                    if not pData:
                        break

                    data += pData + tData + bData

                    pi += positionStride
                    ti += texcoordStride
                    bi += blendStride

    with open(dir + modName + '.vb0', 'wb') as output_file:
        output_file.write(data)

    print('success')

