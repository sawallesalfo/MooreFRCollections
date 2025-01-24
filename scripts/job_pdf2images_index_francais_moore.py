from pdf2image import convert_from_path

pdf_path = "./dictionnary Index Français Moore/index-francais-moore.pdf"
output_folder = "./dictionnary Index Français Moore/images"
print("start")
images = convert_from_path(pdf_path, dpi=300, output_folder=output_folder, fmt="jpeg")
for i, image in enumerate(images):
    print(i)
    image.save(f"{output_folder}/page_{i + 1}.jpg", "JPEG")
    print(f"Page {i + 1} sauvegardée comme image.")
