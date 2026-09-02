

import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 0. Splitter init
splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=500,
    separators=["\n\n", "\n", ".", " ", ""]
)

# 1. configurando o ambiente
model = "mistral:7b"
file_number = "2"
directory_in = "./in/relatos/relato_unico.md"
directory_out = f"./out/{file_number}_{model}.md"

# 2. processamento do arquivo txt
with open(directory_in, encoding="utf-8") as f:
    texto = f.read()

chunks = splitter.split_text(texto)

# prompt da primeira chunk a ser processada
print(f"Iniciando processamento. Total de chunks: {len(chunks)}")

prompt_sum = f"""
### Input Data
The clinical text is delimited by <text> tags below:
<text>
{texto}
</text>

### Role
You are a helpful clinical assistant.

### Instructions
Based ONLY on the text above, WITHOUT INFERENCES, WITHOUT ADDITIONS OF OUTSIDE MEDICAL KNOWLODGE AND WITHOUT CREATING DIAGNOSIS IF IT WAS NOT MENTIONED provide a summary of the following topics:

## 1. Clinical Database
Separe and include the information about the folowing topics, if the information was present in the dialog:
- X-ray or imaging conclusions:
- Triage data (such as blood pressure, heart rate, temperature, or other vitals):
- Recurring medications or allergies:
- Family history or personal medical history:
- Pacient habit and behaviour related to the conditions:
- Demographic characteristics (age range, gender, region):
- Physical conditions noted by the doctor during the examination:
*Note: If one of the topics is not explicit said, add 'not mentioned'.*

## 2. Problem List
List only problems explicitly mentioned. Format as:
- [Problem Name]: (List all the Diagnosis, Physiological Finding, or Symptom). 
*Note: If no explicit diagnosis exists, leave the diagnosis section blank.*

## 3. Plan
For each numbered problem in section 2, provide:
- Possible diagnostic:
- Additional exam test or medical referral (if nedded):
- Treatment plan (Medications, procedures):
- Missing details (Information the doctor still needs to collect):
*Note: If one of the topics is not explicit said, add 'not mentioned'.*
"""

# chama modelo local via Ollama e processa a 1 chunk
response = ollama.generate(model=model, prompt=prompt_sum)
note_sum = response['response']


# 2. chama modelo local via Ollama e itera sobre os demais chunks atualizando o resumo
for i in range(1, len(chunks)):
    print(f"Atualizando resumo com o chunk {i+1}/{len(chunks)}...")
    # 3. Criar prompt da update de chunk
    prompt_update = f"""
    ### Current Summary (Existing Context)
    <existing_summary>
    {note_sum}
    </existing_summary>

    ### New Text Chunk (To be integrated)
    <new_chunk>
    {chunks[i]}
    </new_chunk>

    ### Role
    You are a helpful clinical assistant.

    ### Instructions
    1. INTEGRATE: Compare the New Chunk with the Existing Summary.
    2. UPDATE: Add new symptoms, labs, or plans that were not mentioned before.
    3. REFINE: If the New Chunk provides more detail or corrects a previous finding (e.g., a definitive diagnosis replacing a suspicion), update the information.
    4. DO NOT INFER: If the new chunk doesn't add anything, keep the existing summary as is.
    5. NO DUPLICATES: Do not list the same exam or problem twice.

    ### Output
    Provide the updated version of the summary following the same structure (Database, Problem List, Plan).
    """

    # 3. Chama o modelo para iterar e gerar uma nova resposta
    response = ollama.generate(model=model, prompt=prompt_update)
    note_sum = response['response']

prompt_verify = f"""
    ### Current Summary
    <summary>
    {note_sum}
    </summary>

    ### Original Dialog
    <dialog>
    {texto}
    </dialog>

    ## Verification
    Check if all the information written in the summary is explicitly in the original dialog. Check if everything is correct. If not, remove it and generate a corrected version.
"""

response = ollama.generate(model=model, prompt=prompt_update)
note_sum = response['response']

# 4. Mostrar saída
print("Resposta do modelo:\n")
print(note_sum)

# 5. (Criar e) salvar saída em arquivo txt
with open(directory_out, 'w', encoding="utf-8") as f:
    note_structed = "'''\nCOMENTÁRIOS PESSOAIS (ARQUIVO "+file_number+")\n Modelo: "+ model + "\n Tipo: Relatório feito com um só prompt, com chuncks \n Chunk size: "+str(splitter._chunk_size) + "\n Overlap: "+str(splitter._chunk_overlap) +"\n'''\n\n\n" + note_sum
    f.write(note_structed)
