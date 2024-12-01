from pdf2image import convert_from_path

pdf_path = "./Dictionnary Edition Janvier 2017, Compilé par Urs Niggli/Dictionnaire.pdf"
output_folder = "./Dictionnary Edition Janvier 2017, Compilé par Urs Niggli/images"
print("start")
images = convert_from_path(pdf_path, dpi=300, output_folder=output_folder, fmt='jpeg')
for i, image in enumerate(images):
    print(i)
    image.save(f"{output_folder}/page_{i + 1}.jpg", "JPEG")
    print(f"Page {i + 1} sauvegardée comme image.")
