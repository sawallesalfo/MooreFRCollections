BUCKET_NAME = "moore-collection"
SOURCE_FOLDER = "segmented_audios"
SYSTEM_PROMPT = """Given the audios uploaded, find the best transcription in Moore between the choices I give you. When none of choices,  grade shoul be -1. Else grade 1. 
 Return results in tag <output></output> <grade><grade>.When multiples choices, separate values with `,`. First element of the list is generally a god answers."""
MODEL_NAME = "gpt-4o-mini-audio-preview-2024-12-17"
BATCH_SIZE = 50
