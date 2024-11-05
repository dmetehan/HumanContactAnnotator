# HumanContactAnnotator

In dyadic interactions, observing physical contact between interactants is crucial to understand the nature and quality of their interaction. To facilitate the systematic annotation of physical contact from images, we developed Human Contact Annotator, an intuitive tool to label body parts in contact. The tool is publicly available to enable research into analyzing contact signatures and physical contact in dyads during close proximity interactions. In addition to annotating body region-based contact signatures, our tool allows for informative contact segmentation visualizations, which provide quick insights into the nature of touch over an extended period.

You can find our unimodal method [Pose2Contact](https://github.com/dmetehan/Pose2Contact) and multimodal approach [Image2Contact](https://github.com/dmetehan/Image2Contact) presented in the paper "Decoding Contact: Automatic Estimation of Contact Signatures in Parent-Infant Free Play Interactions".

## Installation

* Python 3.8+ (https://www.python.org/downloads/)
* If you have git installed:
  > git clone https://github.com/dmetehan/HumanContactAnnotator.git
  * Otherwise, download https://github.com/dmetehan/HumanContactAnnotator/archive/refs/heads/main.zip and unzip
* Inside the HumanContactAnnotator folder:
  > pip install -r requirements.txt
* > python main.py

## Usage

* Annotating Contact Signatures:

  ![Annotation Tool](imgs/gui2.png)
* Visualizing Region Contact Frequencies:

  ![Annotation Tool](imgs/gui-heatmaps.png)
* Calculating Inter-annotator Agreement:

  ![Interannotator Agreement](imgs/gui-results.png)

## Citation

To cite our work on HumanContactAnnotator:
```
@inproceedings{doyran2024decoding,
  title={Human Contact Annotator: Annotating Physical Contact in Dyadic Interactions},
  author={Doyran, Metehan and Salah, Albert Ali and Poppe, Ronald},
  booktitle={Proceedings of the 26th ACM International Conference on Multimodal Interaction},
  year={2024}
}
```
To cite our work on detecting contact signatures:
```
@inproceedings{doyran2024decoding,
  title={Decoding Contact: Automatic Estimation of Contact Signatures in Parent-infant Free Play Interactions},
  author={Doyran, Metehan and Salah, Albert Ali and Poppe, Ronald},
  booktitle={Proceedings of the 26th ACM International Conference on Multimodal Interaction},
  year={2024}
}
```
