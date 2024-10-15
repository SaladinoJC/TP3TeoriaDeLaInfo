import sys
import heapq
import time
from collections import Counter

class Node:
    def __init__(self, byte=None, freq=None, left=None, right=None):
        self.byte = byte
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def create_huffman_tree(frequencies):
    heap = [Node(byte, freq) for byte, freq in frequencies.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)

    return heap[0]

def generate_codes(node, prefix="", codebook=None):
    if codebook is None:
        codebook = {}

    if node.byte is not None:
        codebook[node.byte] = prefix
    else:
        generate_codes(node.left, prefix + "0", codebook)
        generate_codes(node.right, prefix + "1", codebook)

    return codebook

def bits_to_bytes(bits):
    byte_arr = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        byte_arr.append(int(byte, 2))
    return byte_arr

def bytes_to_bits(byte_arr):
    bits = []
    for byte in byte_arr:
        bits.append(f'{byte:08b}')  # Convertimos el byte a una cadena binaria de 8 bits y lo agregamos a la lista
    return ''.join(bits)  # Al final, unimos todos los elementos en una sola cadena

def compress_file(original, compressed):
    with open(original, 'rb') as f:
        data = f.read()

    # Contar las frecuencias de los bytes
    frequencies = Counter(data)

    # Crear el árbol de Huffman
    huffman_tree = create_huffman_tree(frequencies)

    # Generar el código de Huffman para cada byte
    huffman_codes = generate_codes(huffman_tree)

    # Codificar los bytes
    encoded_data = ''.join(huffman_codes[byte] for byte in data)

    # Calcular el número de bits de relleno necesarios
    padding = 8 - len(encoded_data) % 8
    encoded_data += '0' * padding

    # Guardar el archivo comprimido
    with open(compressed, 'wb') as f_out:
        # Guardar las frecuencias de los bytes
        f_out.write(len(frequencies).to_bytes(2, 'big'))  # Cantidad de bytes distintos, ahora con 2 bytes
        for byte, freq in frequencies.items():
            f_out.write(bytes([byte]))  # Byte
            f_out.write(freq.to_bytes(4, 'big'))  # Frecuencia (4 bytes para números grandes)

        # Guardar el número de bits de relleno
        f_out.write(bytes([padding]))

        # Guardar los bits comprimidos
        byte_data = bits_to_bytes(encoded_data)
        f_out.write(byte_data)

    print(f"Archivo comprimido guardado como {compressed}")

def decompress_file(compressed, original):
    try:
        # Abrir el archivo comprimido para lectura
        with open(compressed, 'rb') as f_in:
            # Leer la cantidad de bytes distintos (2 bytes)
            num_bytes = int.from_bytes(f_in.read(2), 'big')
            frequencies = {}
            
            # Leer las frecuencias de los caracteres
            for _ in range(num_bytes):
                byte = f_in.read(1)[0]  # Leer el byte
                freq = int.from_bytes(f_in.read(4), 'big')  # Leer la frecuencia (4 bytes)
                frequencies[byte] = freq

            # Reconstruir el árbol de Huffman
            huffman_tree = create_huffman_tree(frequencies)

            # Leer el número de bits de relleno
            padding = f_in.read(1)[0]

            # Leer los bits comprimidos
            byte_data = f_in.read()    
            # SE TRABA ACA VER
            encoded_data = bytes_to_bits(byte_data)

            # Eliminar los bits de relleno
            encoded_data = encoded_data[:-padding]

        # Decodificar el archivo binario usando el árbol de Huffman
        decoded_data = bytearray()
        node = huffman_tree
        for bit in encoded_data:
            node = node.left if bit == '0' else node.right
            if node.byte is not None:
                decoded_data.append(node.byte)
                node = huffman_tree

        # Ahora creamos y escribimos el archivo descomprimido ('original') desde cero
        with open(original, 'wb') as f_out:
            f_out.write(decoded_data)

        print(f"Archivo descomprimido guardado como {original}")

    except FileNotFoundError:
        print(f"Error: El archivo comprimido '{compressed}' no fue encontrado.")
    except Exception as e:
        print(f"Error durante la descompresión: {e}")

def main():
    if len(sys.argv) != 4:
        print("Uso: python Tp3 {-c|-d} original compressed")
        sys.exit(1)

    flag = sys.argv[1]
    original = sys.argv[2]
    compressed = sys.argv[3]

    if flag == '-c':
        start_time = time.time()
        compress_file(original, compressed)
        end_time = time.time()  # Fin del tiempo de compresión
        elapsed_time = end_time - start_time
        print(f"Tiempo de compresión: {elapsed_time:.4f} segundos")
    elif flag == '-d':
        start_time = time.time()
        decompress_file(original, compressed)
        end_time = time.time()  # Fin del tiempo de compresión
        elapsed_time = end_time - start_time
        print(f"Tiempo de decompresión: {elapsed_time:.4f} segundos")
    else:
        print("Flag inválido. Usa -c para comprimir o -d para descomprimir.")
        sys.exit(1)

if __name__ == "__main__":
    main()