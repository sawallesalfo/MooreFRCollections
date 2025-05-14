---
license: mit
pretty_name: MooreFRCollections
dataset_info:
  features:
  - name: moore
    dtype: string
  - name: french
    dtype: string
  - name: source
    dtype: string
  splits:
  - name: train
    num_bytes: 11702967
    num_examples: 50622
  download_size: 5812587
  dataset_size: 11702967
task_categories:
- text-generation
- text2text-generation
- translation
- text-to-speech
language:
- af
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
---

# **MooreFRCollections - Jeu de données bilingue Mooré-Français**

**MooreFRCollections** est un projet ouvert dédié à la création d’un corpus bilingue **Mooré-Français** pour la recherche et le développement de technologies linguistiques adaptées au contexte burkinabé. L’objectif est de fournir un outil essentiel pour tester, entraîner, et affiner des modèles de traduction et d’autres applications d’apprentissage automatique. Ce projet met en avant le Mooré, une langue locale du Burkina Faso.

---

## **Sources de données**
Le corpus a été construit à partir de :
1. **Textes bibliques de JW.ORG** : Contenus collectés (https://www.jw.org//) à l'aide de l’outil [jwsoup](https://pypi.org/project/jwsoup/) pour une extraction efficace des données textuelles.
2. **Dictionnaires bilingues** : 
- Urs Niggli (édition janvier 2017),  Pour l'extraction, j'utilise cette méthode que vous trouvez dans l'article ci-après :[blog](https://sawallesalfo.github.io/blog/2024/11/24/adieu-ocr-place-aux-llm-multimodaux-pour-lextraction-des-informations-dans-les-documents/)
- Dictionnaire de montivilliersnassere disponible  [ici](https://www.montivilliersnassere.fr/actusnasre.html).
- On en cherche toujours :)
3. **Declarations des droits humains**
  - [version française ici](https://www.ohchr.org/sites/default/files/UDHR/Documents/UDHR_Translations/frn.pdf)et [version mooore](https://www.ohchr.org/sites/default/files/UDHR/Documents/UDHR_Translations/mhm.pdf)
 
4. Smol dataset : https://huggingface.co/datasets/google/smo

5. Masakhane dataset: https://github.com/masakhane-io/lafand-mt/blob/main/data/json_files/
  

Pour le moment, **les données sont exclusivement textuelles**, mais elles sont soigneusement nettoyées et formatées pour les rendre compatibles avec les outils modernes d’apprentissage automatique.

---

## **Chargement du jeu de données**
Le jeu de données est disponible sur HuggingFace et peut être facilement chargé avec la bibliothèque `datasets` :

```python
from datasets import load_dataset

dataset = load_dataset('sawadogosalif/MooreFRCollections')
```

---

## **Applications**
Les possibilités offertes par MooreFRCollections incluent :
- **Traduction automatique** : Développement et évaluation de systèmes de traduction Mooré-Français.
- **Recherche linguistique** : Analyse des structures linguistiques uniques au Mooré.
- **Apprentissage supervisé** : Entraînement de modèles pour des tâches spécifiques en Mooré.
- **Applications éducatives** : Aider les enseignants, étudiants et locuteurs du Mooré à explorer les interactions entre leur langue et le français.

---

## **Appel à contributions**
Nous cherchons à élargir et améliorer ce jeu de données. **Vous pouvez contribuer de différentes manières** :
- **Partager des textes en Mooré ou bilingues (Mooré-Français)**.
- **Participer à l’annotation ou à la validation des traductions existantes**.
- **Proposer des idées pour enrichir le projet**, comme des approches de collecte de données ou des applications potentielles.

📩 **Contactez-nous** pour participer ou échanger sur vos idées : [salif.sawadogopro@gmail.com](mailto:salif.sawadogopro@gmail.com). Toute aide ou suggestion est la bienvenue !

Pour contribuer directement via HuggingFace, vous pouvez suivre ces étapes :
1. **Configurer votre environnement de travail** : Assurez-vous que votre dépôt est configuré correctement avec HuggingFace.
   - [Guide sur la dépréciation des mots de passe Git](https://huggingface.co/blog/password-git-deprecation)
   - [Documentation sur la sécurité Git SSH](https://huggingface.co/docs/hub/security-git-ssh)
2. **Changer l'URL distante pour HuggingFace** :
   ```bash
   git remote set-url origin git@hf.co:datasets/sawadogosalif/MooreFRCollections/
   ```
3. **Créer une nouvelle branche pour contribuer** :
   ```bash
   git checkout -b nom-de-votre-branche
   ```
4. **Faire un push de vos modifications** et soumettre une demande de fusion pour revue.

Nous vous encourageons à **demander l'accès à la branche de développement** pour y apporter vos contributions.

---

## **Citation**
Si vous utilisez ce jeu de données dans vos projets, veuillez citer comme suit :

```
@dataset{moorefr2024,
  author       = {Salif Sawadogo,  peut-être toi le prochain},
  title        = {MooreFRCollections: A Bilingual Dataset for Mooré-French Translation},
  year         = 2024,
  url          = {https://huggingface.co/datasets/sawadogosalif/MooreFRCollections}
}
```

---

## **Objectifs futurs**
Bien que le corpus soit actuellement centré sur les **textes**, nous envisageons :
- L’expansion vers des données multimodales (texte associé à des images).
- Une collaboration avec des institutions burkinabé pour garantir la diversité des données.
- La création d’outils pour faciliter l’apprentissage du Mooré par des locuteurs francophones et vice versa.

**Vos idées comptent !** Si vous avez des suggestions ou des propositions de collaboration, n’hésitez pas à nous écrire. Ensemble, faisons avancer le Mooré dans les technologies modernes.

---
