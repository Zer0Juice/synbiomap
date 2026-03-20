---
source: 2025_Who_is_using_AI_to_code_Global_diffusion_and_impact_of_generative_AI.pdf
pages: 69
extractor: pdftext
tokens_raw: 33283
tokens_compressed: 29738
compression: 11%
---

Who is using AI to code?

Global diffusion and impact of generative AI

Simone Daniotti∗1,2, Johannes Wachs3,4,2, Xiangnan Feng2

, and Frank Neffke2,5

arXiv:2506.08945v2 [cs.CY] 20 Nov 2025

1University of Utrecht
2Complexity Science Hub
3Corvinus University of Budapest
4ELTE Centre for Economic and Regional Studies
IT:U Interdisciplinary Transformation University

Generative coding tools promise big productivity gains, but uneven uptake
could widen skill and income gaps. We train a neural classifier to spot AI-generated
Python functions in over 30 million GitHub commits by 170,000 developers, tracking
how fast —and where— these tools take hold. Today, AI writes an estimated
29% of Python functions in the US, a modest and shrinking lead over other countries.
We estimate that quarterly output, measured in online code contributions,
has increased by 3.6% because of this. Our evidence suggests that programmers
using AI may also more readily expand into new domains of software development.
However, experienced programmers capture nearly all of these productivity and
exploration gains, widening rather than closing the skill gap.

∗Corresponding author: daniotti.simone@gmail.com
According to proponents, Artificial Intelligence (AI)—in particular generative AI (genAI)—
will drastically increase our productivity and revolutionize the way we work. For instance, genAI
is expected to complement or substitute humans in an increasing set of tasks [1]. This forces
individuals, firms, and policymakers to make important decisions about the use and regulation of
genAI under major uncertainty. The stakes are high: genAI has become widely accessible through
tools such as ChatGPT or Claude, directly complements human thinking [2], and holds the potential
of becoming a general-purpose technology that can solve a wide variety of problems [3].

Experimental and quasi-experimental evidence so far supports the notion that genAI has transformative
potential, showing that genAI leads to increases in productivity and output of individual
workers in a variety of jobs [1, 4, 5, 6]. Surveys and data reported by Large Language Model
(LLM) owners suggest that these technologies are diffusing rapidly [7, 8, 9]. Yet, estimates of
the aggregate impact of AI on gross domestic product (GDP) and employment are often modest
[10, 11], suggesting that we are far from having a clear picture of the overall impacts of AI.

We do know that there is significant heterogeneity of adoption which could lead to economic
divergence. Although use of genAI is widespread in the working age population, self-reported
adoption rates differ markedly across demographics, seniority, work experience, and sectors [8, 9].
Evidence from job ads and firm websites suggests that adoption of genAI varies across geography
[12, 13]. If genAI indeed substantially raises productivity, any implied barriers to adoption will have
significant consequences for inequality within and across countries [14]. Historically, macro-level
productivity effects of general-purpose technologies, such as steam engines, electricity, and computers,
have taken long to materialize [15, 4, 16, 17]. Together, this leads to substantial uncertainty
about the impact of genAI today.

Resolving this uncertainty requires accurately determining adoption rates, intensity of use, and
productivity effects at a global level. Surveys demonstrating demographic and sectoral heterogeneities
in genAI adoption focus on single countries [8, 9]. Previous work comparing AI adoption
in different countries using survey data finds evidence of differences within and between countries
[18], but differences in sample weighting and analysis periods of the surveys limit our ability to
directly compare observed rates. In the context of genAI, respondents may under-report usage,
especially at work, to avoid judgment [19, 20]. Nevertheless, surveys provide a valuable resource
for understanding adoption patterns. Similarly, randomized controlled trials (RCTs) [21, 6, 1, 4, 5]

and natural experiments [22, 23, 24] are indispensable because they measure causal effects of
genAI adoption by design. However, they typically consider individuals as “treated” whenever they
have access to genAI tools, leaving the extent to which treated individuals used genAI during the
experiments unknown. Moreover, surveys and experiments tend to observe individuals over short
time periods, which limits our ability to know the dynamics of adoption and to observe effects of
adoption that materialize more slowly.

To begin to address these gaps, we ask if we can measure the adoption and use of genAI in
another way at the level of individuals whom we can track over longer periods of time. If so, what
do such measures tell us about the rate of adoption of genAI? Does this differ across countries and
demographics? How does genAI impact the outputs individuals produce, and how do individual
characteristics such as experience moderate these effects?

To answer these questions, we study genAI use at a fine-grained level in one of its main domains
of application: software development, an important and high-value sector [25, 26] that is uniquely
exposed to genAI [27, 22, 21, 28]. To do so, we design and implement a machine learning classifier
to identify code written with substantial AI assistance in over 30 million software developer
contributions, also known as commits, to open-source Python projects on GitHub. To train this
classifier, we assemble a custom training set, combining existing sources with a procedure that
generates synthetic training data. This allows us to analyze shifting patterns of AI-generated code
at a granular level. We leverage this novel source of micro-data to study how quickly the use of genAI
in coding diffuses in six major countries, how this diffusion relates to demographic characteristics,
and how it affects programming activity in a sample of over 100,000 US software developers.

Detecting AI generated code

To collect a large dataset of coding activity, we gather all commits by about 100k US GitHub users
to Python-based open-source projects, recursively cloning all GitHub directories related to each
project. Next, we add commits from a random sample of 2,000 programmers per year for each of
five other major countries in software development: China, France, Germany, India and Russia.
We then analyze these commits to assess the prevalence of AI-generated code (see Materials and
Methods).

Figure 1 describes how we classify these code contributions as either human or AI generated.
We limit this analysis to blocks of code that represent functions to focus on a fine-grained, selfcontained,
yet substantial unit of code. We first construct a ground truth dataset (Fig. 1A), collecting
Python functions of which we are certain they were written by a human programmer. To do so,
we take functions written in 2018, as they predate the release of capable genAI models. Because
programming styles evolve over time, we add functions created in later years from the HumanEval
datasets for the years 2022 and 2024. To add a dataset of similar functions but written by genAI
we apply a two-step procedure. First, for each human-written function we ask one LLM to describe
the function in English, specifying the type of input and output of the function. Second, we feed
this text to a second LLM and request the model to generate a function based on this description.
Our use of two different LLMs —unlike previous approaches [29]— avoids creating unnecessarily
strong correlations between human code and its transcription, while ensuring that the (synthetic)
AI-generated functions in our training data are close in functionality to the original human-written
functions.

Figure 1: Classifying code from functions written in the Python programming language as human or

AI generated. A) Using a collection of human generated code, we ask one LLM to describe the code
in English, then another to implement that description as a Python function. B) We vectorize the
resulting code using GraphCodeBert, an embedding method that uses a code’s tokens, comments,
and variable graph flow. C) We train a neural network classifier combining GraphCodeBert with a
classification head to predict the human/AI labels. D) We evaluate the classifier on out-of-sample
data and apply it to a large database of unlabeled Python functions.

We then train a machine learning classifier on this dataset. Following [30], we transform each
function using GraphCodeBert, a pre-trained language model for code that embeds a function into
a high-dimensional vector space using its tokens, comments, and the dataflow graph of its variables
[31]. The resulting vectors are fed into a classifier to determine whether a given function was written
by a human or by genAI (Fig. 1B-C).

Results

The classifier performs remarkably well, achieving an out-of-sample ROC AUC Score of 0.96
(Fig. S2D) and Average Rate of True positives of 0.95. We apply this classifier to 5 million
functions extracted from 31 million contributions to Python projects from the beginning of 2019
to the end of 2024 for the full population of US-based users and the sampled users in the five
other countries (Fig. 1D). In the Materials and Methods, we show that the classifier also correctly
identifies code generated by more recent LLMs introduced after our data collection ended, as well
as code produced in real-world interactions with LLMs, albeit with somewhat lower accuracy.
Retraining the classifier on code produced by these newer LLMs further improves performance.

Figure 2, panel A plots the AI adoption trajectory for US developers. Adoption rates sharply
increase following major AI advancements, including the launches of Copilot, ChatGPT, and second
generation LLMs. Panel B compares the US to the five other major countries we cover in the global
race toward AI adoption. This shows that the US took an early lead, which it has managed to
maintain ever since. About 29% of Python functions in the US were generated by AI by the end of
2024, closely followed by 23/24% for Germany and France. India draws close at 20%, after having
initially lagged in adoption. In contrast, Russia and China have so far remained late adopters.

Focusing on the full population of US developers, we find that AI adoption rates drop with the
number of years that developers have been active on GitHub. Fig. 3B shows that whereas the most
experienced developers use genAI in 27% of their code, programmers who have just joined the
GitHub platform use these tools for 37% of code. In contrast, using (self-reported) first-name-based
gender inference algorithms, we find no difference between men and women (Fig. 3A).

A

B

Figure 2: Share of AI-generated Python functions over time. A: share of Python functions that
were created or substantially changed by GitHub users in the United States. Vertical lines depict
95% confidence intervals. The plot reveals abrupt shifts in adoption coinciding with key AI-related
events: the release of GitHub Copilot Preview, the public launch of ChatGPT, and the second wave
of LLM releases (GPT4 and related models). B: adoption in China, France, Germany, India and
Russia (note that in China, GitHub competes with the alternative collaboration platform, Gitee[32]).
We sampled 2,000 random programmers per country-year. The US curve is replicated from panel
A as point of reference. The US lead the early adoption of genAI, followed by European nations
such as France and Germany. From 2023 on, India rapidly catches up, whereas adoption in China
and Russia progresses more slowly. 6
To assess how genAI impacts the quantity and nature of code that programmers produce, we
rely on regression models with user and quarter-of-year fixed effects. This compares the output
— in terms of quarterly number of commits — of the same programmer at different points of AI
adoption, controlling for economy-wide trends. These models, summarized in Fig. 3C, suggest a
substantial impact of genAI on developer productivity. We find consistent effects across different
sets of commits: all commits, commits that modify multiple files (which typically require navigating
complex dependencies across scripts), and commits that add new libraries or library combinations
(which typically introduce new functionality to scripts). Moving from 0 to 29% genAI usage—the
estimated US adoption rate by the end of 2024—is associated with a 3.6% increase in commit rates
across all these commit types. However, these associations with user productivity are fully driven
by experienced users, for whom a 29% adoption rate would imply a 6.2% increase in commit rates
(Fig. 3D). In contrast, we observe no statistically significant effects among inexperienced users.

Apart from increasing activity rates, AI adoption is also associated with increased experimentation
with new libraries and combinations of libraries, which [33] interpret as signs of innovation.
Because libraries often focus on specific types of functionality — such as visualization, natural
language processing, web interactions, or database operations — this suggests that genAI helps
programmers expand their capabilities to new domains of software development. At average endof-2024
AI use rates for US developers, our models predict that developers will implement 2.7%

more new combinations of libraries. Results are robust to variations in how we determine new
library introductions. In particular, effects are unlikely due to esoteric libraries (“AI slop”): findings
do not change much if we only use the 5,000 most common libraries or if we group libraries into

124 coarse categories first. Moreover, Fig. S6 of the SI shows that these effects, as well as the
earlier productivity effects, are likely lower bounds because errors in the measurement of users’ AI
adoption rates bias each of these estimates downwards.

A B

C

D

Figure 3: A) Intensity of genAI use by gender inferred from GitHub display names (US, 2024). B)

Intensity of genAI use by user tenure (US, 2024). C) Estimated effect of genAI use on user activity
from a user-quarter panel regression with user and quarter fixed-effects. GenAI use is associated
with increased commit activity across all commits, multi-file commits (“Multi-File”) that navigate
project interdependencies, and commits adding library imports (“Imports”), which we interpret as
adding new features. GenAI is also associated with wider ranges of individual libraries (“Indiv.
Libs”) and library combinations (“Combos”), and increased experimentation with new libraries or
combinations. Results hold subsetting on the 5,000 most common library combinations (“Combos
(Top 5k)”) and coarsened library categories (“Combos (Groups)”). Error bars: 95% confidence
intervals (standard errors clustered by user).

Discussion

We set out to measure the use of genAI at the micro-level, in order to study its diffusion and its
consequences at a global scale. Focusing on the software development labor force, we demonstrated
how genAI has diffused and how this has affected the quantity and nature of code that programmers
produce. To do so, we developed a new genAI classifier to identify AI-generated functions in
GitHub commits. Applied to a large dataset covering software development activity across major
countries, we document noticeable growth spikes in genAI-generated code soon after key genAI
releases. Yet, we also observe significant differences between countries. Corroborating existing
studies [8, 9], our estimated adoption rates are higher among less experienced programmers but
unlike most previous work, we find no significant differences between men and women.

We also find that genAI reshapes both the volume and nature of programming work. Using
within-developer variation—comparing the same programmer before and after adopting genAI—we
show that AI adoption substantially increases output. Developers using genAI are also more likely
to incorporate novel combinations of software libraries into their code, suggesting they venture into
new technical domains [33] using unfamiliar building blocks [34]. However, both productivity and
exploration gains concentrate almost exclusively among more experienced developers.

How do our findings compare to prior findings? Our estimates of the most recent adoption
rates in the US of around 29% are remarkably similar to adoption rates claimed for coding work at
Microsoft 1 and Amazon 2. This shows that, despite our focus on code from open source Python
libraries, our results closely align with estimates of adoption rates from other contexts and may
generalize beyond the specific setting of this study.

Unlike most other studies, our design allows us to compare adoption rates across countries. Here,
we find a clear and sustained lead by US programmers. Use of LLMs may be lower in countries
like China and Russia because providers such as OpenAI and Anthropic block access (supply side)
and censorship limits local use (demand side), even though many users connect using VPNs [35].
However, other major countries are quickly catching up, eroding the US’ first-mover advantage.
Another aspect that sets our study apart is that existing literature typically focuses on access to
genAI — yielding reduced-form estimates of the causal effect of the so-called intention-to-treat,
1https://cnb.cx/3YorqDQ
2https://www.nytimes.com/2025/05/25/business/amazon-ai-coders.html

not of genAI itself — or usage in controlled experimental settings. In contrast, our approach allows
us to quantify the intensity with which the technology is used in real-world work activities. Finally,
we note that our cross-country evidence on genAI use complements firm-level survey work on
broader AI adoption which extends back to before the genAI era [18]; while levels are not directly
comparable, both perspectives document persistent cross-country gaps in AI use.

When it comes to the productivity effects of genAI, our estimates are generally smaller than those
found in RCTs [36, 6] and studies exploiting natural experiments [22, 24]. In robustness checks (SI
section S4) we study whether nonlinearities or threshold effects in the benefits of genAI adoption
can explain such discrepancies, but find little significant evidence for this hypothesis. A more
promising explanation is measurement error, which is likely to bias effect estimates downwards.
In line with this, Fig. S6 of the SI shows that our effect estimates increase substantially if we
correct them for measurement error. Moreover, we show that effects concentrate in experienced
programmers, while junior developers seem not to benefit much from genAI. The higher effect
estimates in prior literature may therefore also reflect differences in the populations and complier
samples they studied.

There are several limitations to our study. First, our analysis focuses on software development.
Although this limits its scope, work in this sector is uniquely amenable to quantitative analysis
at a level of granularity that is required to study how AI affects workers and their tasks. Within
software, we focus only on Python-based open-source contributions. While Python is a widely
used language, adoption patterns may differ in other programming ecosystems. We argue that
estimates derived from open-source Python code on GitHub are economically meaningful, because
open source software (OSS) underpins most commercial stacks and carries large measured value

[34, 37]. GitHub’s central role in collaboration, networking, and signaling further ties our evidence
to professional activity [38, 39]. Finally, that our estimates of AI use in the US line up closely
with reported AI use at leading US firms mentioned above increases our confidence in the external
validity of our findings.

More generally, we also do not account for potential externalities between coworkers or heterogeneity
in productivity across firms, all of which may be relevant factors in how genAI affects

programming activity. Beyond firms, our geographic analysis is limited to a subset of countries
and it would be important to widen the analysis to include countries at different income levels.

In the specific case of China — where the programming community also relies on an alternative
collaboration platform, Gitee [32] — there is some additional risk that our focus on GitHub projects
distorts estimates. Finally, when it comes to the effects of genAI, there are many other ways to
evaluate the productivity of programmers that heed more attention to code quality, from tracking
how issues get resolved and code merges to the implemented test coverage. While feasible in principle,
such analysis requires new data collection and careful design of metrics. We therefore leave
questions of the effect of genAI on code quality for future research.

How much value has genAI created in coding? While hard to answer definitively, our study
offers some important pieces of this puzzle. Based on an analysis of detailed task surveys and wage
statistics for about 900 different occupations, we estimate that the US spends between 637 and
1,063B USD on labor costs related to coding activities per year (SI, section S6). Assuming our
estimated diffusion rates of 29% by the end of 2024 (based on open-source Python contributions)
are representative of code in general, the annual value generated by genAI coding assistants in the
US would depend on how much they increase productivity. Using our own, conservative, baseline
estimates, genAI would have increased the volume of commits by 3.6%. Assuming these commits
reflect valuable code contributions, our calculation implies that genAI generates 23–38B USD
of additional code per year. This estimate treats productivity gains as similar across programming
languages. In a more conservative scenario, where productivity effects outside Python are negligible,
the value of genAI would drop to about 17% of this figure (approximately 4–6B), using estimates
of Python’s share of GitHub code [40].

By contrast, various lab experiments [21, 36] and field experiments [6] in software development
all yield substantially larger causal effects of genAI on task completion times — arguably a more
relevant quantity to track than commit volumes. Averaging across such studies (see Materials and
Methods for details) yields an estimated 6.0%-15.7% increase in productivity at a 29% adoption
rate, translating into a range of 38-167B USD for the direct impact of genAI on US coding activities.
However, these estimates ignore that genAI may also lead to a reduction in the market price of code.
Because this yields cost savings for consumers of code, while reducing profits for suppliers (i.e.,

programmers), factoring in such general equilibrium effects further widens the range of possible
outcomes (SI section S7). In the Materials and Methods section we show that this would mostly
affect the upper bound of our estimates, with lower bounds all but unaffected. The upshot of these

back-of-the-envelope calculations is that, although the total value of genAI to the US economy is
uncertain, it is most likely substantial, on the order of at least tens of billions of USD.

Given that genAI has diffused quickly beyond the US, global cost savings would be larger still,
even if we confine ourselves to the software sector. Moreover, we are currently still in the early
phases of the diffusion curve of what looks to be a new general purpose technology [3]. Historically,
early-stage productivity effects of general purpose technologies have been hard to identify because
it takes time to integrate them into firm level workflows and procedures, train individuals and amass
the complementary assets needed to fully exploit their potential. Based on this, we find ourselves
on the bullish side of the debate when it comes to the productivity effects of genAI.

Our results on such effects and the heterogeneous diffusion of genAI raise important questions
for policymakers and researchers. We need to understand the barriers of adoption to AI: are these
similar to prior radical innovations [41] or is this time different? Additionally, these barriers need
to be understood not only at the individual level, but also at the firm, regional, and national levels.
Our study takes a first step toward answering such questions.

Moreover, given the wide dispersion in productivity across programmers [42, 43, 44] and
our finding that benefits accrue to more experienced coders only, future research should explore
how AI adoption affects developer activity at the upper tail of elite programmers, where the most
significant breakthroughs and innovations are likely to occur. Finally, our study exclusively focused
on programming tasks. Yet, one study of elite software developers suggests that access to genAI
leads to a shift from managerial tasks to coding [22], suggesting that an important margin along
which productivity effects materialize is shifts in the task composition of software developer jobs.

The nature of work often changes with the introduction of new technologies. Understanding
these changes is especially difficult when the innovation in question is radical [41], such as the
spinning jenny, transistors, or robots, and at the same time pervasive [45]. The uncertainty of the
effects of genAI on work and labor markets is reflected in the wide range of attitudes researchers
and policymakers take towards it, ranging from utopian to skeptical and outright apocalyptic. These
attitudes are formed in a fast-moving context, and are based on incomplete evidence on the adoption
and effects of AI. The findings in this study provide better evidence of how genAI is used in a large,
important, and highly exposed sector of the economy, as well as a way to monitor this in real-time
going forward. Applying our AI detection classifier to millions of code contributions made over a

six-year period, we can confirm that AI adoption is fast, but heterogeneous across countries and
individuals. Moreover, AI adoption is associated with increased activity rates in online software
development collaborations.

However, one of the most surprising findings is the fact that genAI increases experimentation
with new libraries, suggesting that genAI allows users to advance faster to new areas of programming,
embedding new types of functionality in their code. This corroborates prior findings [46]
that genAI increases individual innovation, pushing individuals’ capabilities in terms of the use of
new combinations of libraries. However, again only experienced users seem able to leverage genAI
in this way, with important consequences for programmers’ ability to master new coding skills in
the presence of genAI.

Acknowledgments

We thank Ulrich Schetter, Hillary Vipond, Andrea Musso, and participants of the ANETI Brownbag
seminar for helpful comments. We thank Marton Salamon for valuable research assistance. ´

Funding: F. N., S.D., J.W. and X.F. received financial support from the Austrian Research
Promotion Agency (FFG) in the framework of the project ESSENCSE (873927), within the funding
program Complexity Science. JW also acknowledges financial support from the Hungarian National
Scientific Fund (OTKA FK 145960).

Author contributions: S.D. and F.N. conceptualized the research. S.D. implemented the primary
method. S.D. and J.W. collected the data. X.F. collected data and estimated the volume of the U.S.
programming-related wage sum. All authors analyzed the data. F.N. and J.W. led in drafting the
manuscript. All authors contributed to the writing of the manuscript.

Competing interests: There are no competing interests to declare.

Data and materials availability: Code and data to replicate our analyses are available here: this
link

Supplementary Materials for

Who is using AI to code?

Global diffusion and impact of generative AI

Simone Daniotti∗

, Johannes Wachs, Xiangnan Feng, Frank Neffke

This PDF file includes:
Materials and Methods
Supplementary Text
Figures S1 to S9
Tables S1 to S28

S1 Materials and Methods

Data

Data and code to reproduce the results in this paper are available at this link. The datasets contain
the following columns: anonymized user ID, anonymized ID of the modified function, anonymized
project name, anonymized commit ID, estimated (corrected, see section S1.3) AI probability, and
the user’s self-reported country.

Our data collection proceeds as follows. First, we collect all users who have made a commit to
public repositories on GitHub using the GHArchive dataset hosted on Google BigQuery, focusing
on the period 2019-2024. Then, we geolocate GitHub users using self-reported locations in GitHub
profiles obtained through the GraphQL API [47]. Fig. S1 of the SI shows that the distribution
of users across countries derived from self-reported data closely matches the same distribution
derived from users’ IP addresses as provided in the GitHub Innovation Graph dataset (https:
//innovationgraph.github.com/).

Next, we collect commits by users that report US locations to projects that use Python as their

S1
programming language. To do so, we select all users that are active in such projects in a given year.
Next, in each year, we recursively clone all GitHub directories related to these users and obtain all
commits to projects where the user makes over 3 commits in the year. Finally, we analyze these
commits using the PyDriller tool [48]. To manage computational expenses, AI usage in the other
five countries of Fig. 2B is based on random samples. We draw these samples from populations that
are created analogously to the one for the US. From each population, we sample 2,000 programmers
per country per year. This yields a total of 70,000 user-year observations.

A B

Figure S1: Location of GitHub users. A: Self-reported locations of GitHub users. B: Number of
users in each country based on self-reported locations against IP addresses.

Detecting Generative AI in code

To detect the use of genAI, we focus on self-contained code blocks that perform well-defined tasks:
functions. For each function, we determine how many lines were modified in a commit. We then
keep only those functions in which modifications occurred in over 80% of lines of code.

S1.1 Training data

The ground truth data on which we train our supervised model for detecting AI-generated Python
functions combines multiple sources. We start by collecting functions created by human coders from

S2
three different datasets. The first dataset randomly samples Python functions from GitHub that were
created before the introduction of genAI coding tools. In particular, we sample python functions
created in 2018. The second and third datasets are HumanEval [49] and HumanEval-X [50], both
of which were originally created to evaluate and measure functional correctness of code. All the

three dataset combined contain almost 4,000 human-written Python functions. Adding the latter
two datasets ensures that the human-made Python functions we use to train our models include
examples created in different years, including years in which genAI tools had become more widely
available. Next, inspired by [29], we generate a synthetic dataset of Python functions written by
different LLMs, using GPT3.5-turbo (50%), GPT-4o-mini (30%) and GPT-4 (20%). To do so, we
create synthetic clones of the human-written functions described above, using an LLM chain that
combines two LLMs, mimicking recent LLM Agent tools. Each LLM performs a different task.
The first LLM is prompted to describe a given human-made function in terms of its functionality

and the structure of the required input and generated output. The second LLM is asked to read this
description, and to then generate a function that accomplishes the same task. The exact prompts and
an example of the output are listed in Table S1 of the SI. The total size of the training set amounts
to around 8,000 functions.

S1.2 Detection model

Our genAI detection model relies on open source components and is set up to efficiently scale to analyze
millions of Python functions. We chose a state-of-the-art technique based on CodeBERT [51].
Our approach resembles that of GPTSniffer [30]. In this paper, the authors train a CodeBERT model
to detect AI-written Javascript programs. We instead aim to detect AI-written Python functions. To
do so, we build a classifier on top of a newer and more advanced version, GraphCodeBERT [31],
which is better able to capture and understand patterns in code. We add a linear layer to the GraphCodeBERT
model to perform a classification task. Finally, we use the training data to finetune all
parameters for optimal model prediction, including to retrain the embedding weights to optimize
results.

Tokenization was performed using GraphCodeBERT’s tokenizer, setting a maximum sequence
length of 512 and applying padding and truncation to maintain consistency across inputs. As a loss

S3
function, we use cross-entropy loss (torch.nn.CrossEntropyLoss), which is well-suited for
classification problems and commonly used in RoBERTa-based classification models. As shown in
Fig. S2, in our case it learns to effectively differentiate between AI-generated and human-written
code. Since the model returns raw logit values, the model internally applies a softmax operation,
comparing the predicted probability distribution with the ground truth labels.

To train the model, we split our ground truth data into training and evaluation sets using an
80/20 ratio with a fixed random seed. We then use the Hugging Face Trainer API to handle training,
evaluation, and optimization. Our training configuration includes 10 epochs, a batch size of 32
per device for both training and evaluation and the AdamW optimizer (adamw hf) with a learning
rate of 1e-5 and weight decay of 0.005. We set warmup steps=1000 to help stabilize learning in
the early phases. Logging occurs once every 100 steps, with evaluation and model check-pointing
at each epoch. In the end, only the best-performing model on the evaluation set is retained. For
reproducibility, we use a fixed data seed (seed 365). As shown in Fig. S2, the model manages to
effectively identify AI generated code in our ground truth data, reaching an out-of-sample ROC
AUC Score of 0.96, Average Precision Score [52] of 0.9685 and Average true positive rate of 0.95
(F1 score 0.8911 with a 0.5 threshold).

Role Prompt

System You are a python expert programmer.

User (Generate description) This is a python script in markdown. Describe the task or tasks

this script is solving, explaining the input and the output specifications
for each function.

User (Code from description) This is the description of a python script. Based on the description,
write a full code that fulfills that task/tasks. The python
script should be organized in a single markdown block. Please
return only the code, do not return any clarifications before or
after the code.

Table S1: System and User Prompts for Synthetic Dataset generation.

S1.3 Estimating AI usage rates

In Fig. 2 and in the regression analyses, we study the diffusion and effects of genAI by quantifying
the probability that a piece of code was written by AI: ( = 1). Our data allow us to estimate a

S4
A B C

D

Figure S2: Detector Prediction Test. Evaluation of the trained detector on a test set. A: predicted
probability that code was AI-generated for human-generated functions. B: predicted probability
that code was AI-generated for AI-generated functions. C: Loss curve during the training of the
detection model. D: ROC Curve of the classifier.
different probability: the probability that our model detects the use of AI in a function: ( = 1).
Using the law of total probability, we can write the latter probability as:
( = 1) = ( = 1| = 1)( = 1) + ( = 1| = 0)( = 0) (S1)
or

( = 1) = ( = 1| = 1)( = 1) + ( = 1| = 0) (1 − ( = 1))
We can estimate some of these terms using our ground truth data set:
• ( = 1| = 1): ˆ
 , estimated probability that AI-generated code is detected to be AI in
S5
the ground truth data (true positive rate)

• ( = 1| = 0): ˆℎ
 , estimated probability that human-written code is detected to be AI

in the ground truth data (false positive rate)

• ( = 1): ,ˆ estimated probability of AI detection (observed quantity)

• ( = 1): ˆ, estimated AI usage rate (quantity of interest)

Using this notation, we can write eq. (S1):

ˆ = ˆ
 ˆ + ˆ
ℎ
 (1 − ˆ)

= ˆ

ˆ
 − ˆ
ℎ

+ ˆ
ℎ

and rearrange terms to arrive at:

ˆ− ˆℎ

ˆ
 − ˆℎ

ˆ =

, (S2)

We can use this equation to correct the estimated AI adoption probabilities from our AI detector

for miss-classification errors. We use this quantity throughout the paper as the estimated AI adoption

rate in a given sample of functions. In doing so, we allow true and false positive rates to differ
across countries, using country-specific correction parameters ˆ
 and ˆℎ
 . As shown in Table
S2, such differences turn out to be modest and most pronounced in false positive rates.

Country False Positive Rate True Positive Rate
United States 0.2321 0.9550
China 0.2405 0.9521
Germany 0.2397 0.9516
India 0.2296 0.9520
Russia 0.2572 0.9617
France 0.1989 0.9519

Table S2: Country-specific estimates of the false positive rate, ˆhum
GT , and true positive rate, ˆ
 .

A consequence of the correction described in eq. (S2) is that adoption rates need not be strictly
positive. This is, for instance, visible in the confidence intervals of the corrected usage rates in

S6
Fig. 2, where the confidence intervals for all countries are centered on zero in the period before the
widespread availability of genAI coding tools.

S1.4 Code Verbosity

Here, we explore whether human coding styles affects the accuracy of AI detection, focusing on
verbosity. In case the AI detector misclassifies verbose human code as AI-generated, we evaluated
whether verbosity or templatedness predict false positives among human-written functions.

To measure verbosity of Python functions, we used individual features common in the software
engineering literature on readability and code style: average line length, blank-line ratio, comment
ratio, docstring length, and token count. These capture layout, documentation, and size dimensions
of code verbosity [53, 54]. We construct two composite measures. The first, Composite Verbosity,
averages standardized values of line length, blank-line ratio, comment ratio, and docstring length,
capturing stylistic and documentation verbosity. The second, Composite Verbosity + Size, adds
standardized token count to these components to incorporate overall code length alongside style and
documentation. Templatedness, representing repetitiveness or boilerplate structure, was measured
as one minus normalized token entropy, following the “naturalness of software” literature [55].
Variable Spearman  t statistic p-value
Average line length -0.017 -0.526 0.599
Blank ratio -0.017 -0.527 0.599
Comment ratio -0.006 -0.186 0.852
Docstring length -0.141 -4.515 < 0.001
# of Tokens 0.109 3.452 < 0.001
Composite Verbosity -0.042 -1.326 0.185
Composite Verbosity + Size -0.010 -0.309 0.757
Templatedness 0.051 1.619 0.106

Table S3: Spearman correlations and associated test statistics measuring the relationship between
measures of code verbosity of human written code and the false classification of the code as AIwritten.We
report two analyses on 1,000 randomly chosen out of sample Python functions written by
humans. We analyze the likelihood that these functions are incorrectly classified as written by AI
(false positives/FP).

S7
Correlations with classifier false-positives (human code classified as AI). Across 1,000 human
functions, none of the individual verbosity features correlate strongly with FP status. The largest
absolute Spearman correlation is -0.14 for docstring length (fewer FPs for more documented code).
Token count shows a mild positive correlation ( = 0.11), and templatedness is weakly positively
correlated ( = 0.05). The composite verbosity indices are near zero (composite verbosity:  =
−0.04; composite verbosity + size:  = −0.01). Overall, verbosity does not systematically relate to
the false-positive rate. We report the correlations and p-values in Table S3.

Composite Verbosity (VS)

Composite Verbosity + Size (VC)

Templatedness

False positive rate (%)

False positive rate (%)

False positive rate (%)

1 2 3 4 5 6 7 8 9 10
Decile

1 2 3 4 5 6 7 8 9 10
Decile

1 2 3 4 5 6 7 8 9 10
Decile

Figure S3: The relationship between code verbosity, operationalized in three ways, and the likelihood
a human-written function is incorrectly classified as AI-written. We split the verbosity scores
into deciles, and plot the mean false positive rate with bootstrapped confidence intervals. We find
no consistent relationship between code verbosity and false positives.

False positives by verbosity decile. When human functions are grouped by verbosity, FP rates
fluctuate around 10% with no monotonic trend, see Fig.S3. This pattern suggests random variation
rather than systematic bias in code verbosity among human-written functions incorrectly classified
as AI written.

S1.5 Value produced by genAI coding assistants

In the discussion section, we provide back-of-the-envelope calculations for the monetary value of
genAI in US coding activities. These calculations start from our estimate that, by the end of 2024,
28.6% of functions from US developers were produced by genAI. Note that we report the estimate
as 29% in the main text but carry out all calculations with the more precise estimate of 28.6%. Based
on our baseline, conservative point estimate of 0.122 for the effect of genAI on commit volumes, a

S8
29% usage rate will translate into an overall increase of
0.122∗0.286 − 1 = 3.55% ≈ 3.6%. We then
analyze detailed task surveys and wage statistics for about 900 different occupations. This yields
that the US spends between an estimated 637 and 1,063B USD on coding-related labor costs per
year (SI, section S6).

If we are willing to assume that (1) our estimated productivity effects (based on open-source
Python contributions) are representative of code in general and (2) that the associated increase in
commits accurately reflects the underlying causal effect on labor productivity of coders — including
that more commits translate into more valuable code — we arrive at a total value of productivity
increases in US coding work of between 23 and 38B USD a year. If, instead, productivity effects are
negligible outside Python, the value of genAI could be as low as 17% [40], of our most conservative
estimate above (i.e., 3.2-5.3B USD). However, not only do we deem this implausible, but absent
additional information, it would also go against the maximum-ignorance stance that we implicitly
took above.

Despite controlling for observed and unobserved user characteristics, our estimation design
is not optimized for identifying causal effects. Moreover, we cannot account for any spillover
effects from genAI usage across workers. In fact, our estimates almost certainly understate the full
economic impact of genAI in software development. Field experiments that track developers in
live codebases report increases of roughly 13.6% in commits and a 26% faster task completion
rate [6]. Natural experiments exploiting the staggered roll-out of GitHub Copilot find that access
to Copilot leads to a 6% increase in merged pull-requests [24] and a 5.5% increase in commits
[22]. In lab experiments, subjects with access to genAI complete software tasks 21-55% faster,
translating to a 6.0%-15.7% effect assuming a 28.6% AI use rate [21, 36]. Combining the average
of the three estimates of improvement in task-completion time from RCTs (55% [21], 21% [36],
and 26% [6]) with our estimated 28.6% AI use rate would imply a 9.7% effect and an annual value
of $62B-$103B USD. Relying instead on the average increased commit and merged pull request
rates across one RCT and two natural experiments (13.6% [6], 5.5% [22], and 5.6% [24]) with the
estimated AI use rate yields an 2.35% increase in productivity or 15B-25B USD in annual value.

Note, however, that none of these estimates account for general equilibrium effects. If genAI
raises worker output, the price of code will drop, leading to savings for its consumers. This in
turn, increases the demand for code. In the SI, section S7, we show that, depending on the exact

S9
assumptions about elasticities and market conditions one is willing to make, total welfare effects
may lie anywhere between 21B and 126B USD based on our own effect estimates, with even larger
gains possible if effects are closer to the ones reported in lab and field experiments. However, the
upper bounds of these estimates refer to the extreme situation where supply of code is perfectly
elastic. This unrealistically assumes that the drop in price now benefits consumers across the entire
volume of code they consume, but does not at all hurt producers of this code. The (equally unlikely)
lower bounds, in contrast, are very close to our initial estimates that do not adjust for general
equilibrium effects. These initial estimates can therefore be considered conservative, also in the
longer run.

Supplementary Information

S2 AI Detector Model Validation

S2.1 Validation on real-world AI-generated code

To evaluate how well our detector recognizes the use of genAI in real-world code, we rely on
conversations with LLMs recorded in the WildChat database [56]. WildChat comprises 1M realworld
user-AI conversations. We focus on conversations containing Python functions, extracting
21k functions for interactions with GPT-3.5-turbo and 12k functions for interactions with GPT-4.

Figure S4 shows how well our detector identifies these functions as AI-generated, using a
random sample of 5,000 functions for each LLM. We study functions created under two separate
conditions. First, we use a sample of functions that were generated in the first round interaction with
the LLMs, so called ”synthetic” functions. Next, we use a sample of functions that were generated
in later rounds of the interaction with the LLMs. We refer to these functions as ”assisted”. The
average probability of true positives is very similar across samples at around 0.7 (GPT-3.5 turbo
— synthetic: 0.701, assisted: 0.698; GPT-4 — synthetic: 0.675, assisted: 0.651). This suggests that
although the AI detector performs somewhat less reliably on AI-generated created by real-world
users, it is unaffected by how much a user interacts with the LLM to generate the code.

S10
A B

C D

Figure S4: AI detection in functions from WildChat. The panels show histograms of the probability
that functions originally created by LLMs were detected as AI-generated. Functions are taken from
interactions of human coders with GPT-3.5 turbo (panels A and B) and GPT-4 (panels C and D)
collected in the WildChat dataset. “Synthetic” code (panels A and C) refers to code generated in the
initial response of the LLM at the start of each interaction. “Assisted code” refers to code generated
in later rounds of the interaction between the human coder and the LLM.

S2.2 Validation on more recent genAI models

Since our data collection ended in 2024, newer LLMs have been introduced. Here, we test the
performance of our detection model on code created by four such models: OpenAI’s GPT-4.1,
Anthropic’s Claude Sonnet 4, and Deepseek-V3. We also test the model on code generated by
OpenAI’s o3, a reasoning model. To do so, we reproduced the procedure depicted in Fig. 1 to
generate an additional 1,000 synthetic functions for GPT-4.1 and o3, and 500 for Claude Sonnet
4 and Deepseek-V3. We then test how well the detector manages to identify these functions as
AI-generated.

S11
A B

C D

E F

G H

Figure S5: Performance of classifier on code generated by recent LLMs. Each panel shows a histogram
of the predicted probability that the classifier correctly identifies functions as AI-generated.
Rows correspond to the LLM used to generate the function: A/B: GPT-4.1; C/D GPT-o3; E/F:
Claude Sonnet 4; G/H: DeepSeek-V3. Panels on the left correspond to predicted probabilities
without retraining the classifier; panels on the right are based on a retrained classifier that uses an
additional 500 training examples of Claude- and Deepseek generated functions.

Results are presented in Fig. S5. The detection model is still predictive, especially for the
newer OpenAI models, but struggles in differentiating between human code and code generated by

S12
either Claude or DeepSeek. Therefore, we add 500 examples of DeepSeek- and Claude-generated
functions to our training set and re-train the model. In the case of o3, performance comes close to the

0.95 average probability of true positives we observed for our initial sample of synthetic functions.
Table S4 shows that adding this modest number of example functions already substantially improves
detection performance, even for the models that were not used in the creation of additional training
data. We therefore expect that by expanding the training set, we may be able to maintain the
detector’s performance also as genAI technologies improve, at least in the near future.
Model Before Training After Training
DeepSeek-V3 0.452 0.561
Claude-Sonnet-4 0.630 0.831
o3 0.867 0.910
GPT-4.1 0.763 0.781

Table S4: Average probability of true positives before and after training.

S3 Cross-country differences

In Fig. 2, we show genAI adoption rates in six major countries in software development with their
95% confidence intervals. To assess to what extent these adoption trajectories differ significantly
across these countries, we first aggregate the data to the country-year level. Next, we run twosided
equality-of-means t-tests, comparing all countries to one another in each year. The results are
summarized in Table S6. In each cell, the table lists the p-values for the comparisons in the associated
country pair. p-values below 0.01 are depicted in bold. Moreover, whenever the row-country’s
adoption rate exceeds the column country’s, the p-value is colored green. Otherwise —when the
column country leads the row country— the p-value is colored red and put in parentheses.

S4 Detailed regression results

To estimate the effect of AI adoption on users’ coding output as well as associations between AI
adoption rates and demographic variables, we first need to determine the adoption rate of a given
user at a given point in time. We focus on US users and drop those users with implausible commit

frequencies, either pushing over 10k commits in total or over 2k commits in a single quarter, as
S13
Table S5: Pairwise p-values for differences in AI adoption rates

2019 China France Germany India Russia United States
China – (0.647) (0.471) (0.925) (0.333) (0.509)
France 0.647 – (0.965) 0.682 (0.778) 0.856
Germany 0.471 0.965 – 0.505 (0.753) 0.700
India 0.925 (0.682) (0.505) – (0.355) (0.552)
Russia 0.333 0.778 0.753 0.355 – 0.472
United States 0.509 (0.856) (0.700) 0.552 (0.472) –

2020 China France Germany India Russia United States
China – 0.196 0.000 0.217 0.104 0.029
France (0.196) – 0.000 0.935 0.501 0.192
Germany (0.000) (0.000) – (0.000) (0.000) (0.000)
India (0.217) (0.935) 0.000 – 0.592 0.401
Russia (0.104) (0.501) 0.000 (0.592) – 0.987
United States (0.029) (0.192) 0.000 (0.401) (0.987) –

2021 China France Germany India Russia United States
China – (0.395) (0.261) (0.170) (0.533) (0.088)
France 0.395 – (0.919) (0.808) 0.764 (0.839)
Germany 0.261 0.919 – (0.870) 0.640 (0.919)
India 0.170 0.808 0.870 – 0.511 0.894
Russia 0.533 (0.764) (0.640) (0.511) – (0.458)
United States 0.088 0.839 0.919 (0.894) 0.458 –

2022 China France Germany India Russia United States
China – 0.000 0.000 0.000 0.001 (0.000)
France (0.000) – (0.129) 0.154 (0.012) (0.000)
Germany (0.000) 0.129 – 0.008 (0.421) (0.000)
India (0.000) (0.154) (0.008) – (0.000) (0.000)
Russia (0.001) 0.012 0.421 0.000 – (0.000)
United States 0.000 0.000 0.000 0.000 0.000 –

2023 China France Germany India Russia United States
China – (0.000) (0.000) (0.944) (0.000) (0.000)
France 0.000 – (0.001) 0.001 (0.000) (0.000)
Germany 0.000 0.001 – 0.000 0.937 (0.000)
India 0.944 (0.001) (0.000) – (0.000) (0.000)
Russia 0.000 0.000 (0.937) 0.000 – (0.000)
United States 0.000 0.000 0.000 0.000 0.000 –

2024 China France Germany India Russia United States
China – (0.000) (0.000) (0.000) (0.000) (0.000)
France 0.000 – (0.852) 0.000 0.000 (0.000)
Germany 0.000 0.852 – 0.000 0.000 (0.000)
India 0.000 (0.000) (0.000) – 0.000 (0.000)
Russia 0.000 (0.000) (0.000) (0.000) – (0.000)
United States 0.000 0.000 0.000 0.000 0.000 –

Table S6: Comparison of mean adoption rates: t-tests. The table reports p-values of t-tests that

compare the mean genAI adoption rate of the row country to the mean adoption rate of the column

country in each year between 2019 and 2024. When these differences are statistically significant

at the 1% level, p-values are bold. Green colors refer to years in which the row country leads the

column country in genAI adoption, red colors the opposite. In the latter case, p-values are put in

parentheses.

S14
likely bots or automated accounts. Next, we calculate the average score from our AI-detection
algorithm — corrected by applying applying eq. (S2) — across all functions produced by a user in
each given quarter. This yields a user-quarter level dataset that describes AI usage rates of 100,097
users over a time span of, on average, 5.1 quarters. Whenever these averages are based on fewer
than 10 functions, the observations are set to missing. In principle, it is also possible to reduce the
number of missing observations by interpolation between non-missing observations. However, this
risks using information from future quarters. To avoid this, we instead fill values forward for at
most 2 quarters. That is, we assume that — absent further information — AI adoption rates remain
constant, at least for a limited amount of time.

S4.1 AI adoption and output

To determine the effects of AI adoption on the quantity and nature of output that GitHub users
produce, we add to our user-quarter level dataset information on the volume and types of commits
that users produce, as well as the libraries they use in these commits. We analyze the effect of
genAI adoption on these variables using fixed effects models. That is, we estimate Ordinary Least

Squared models (OLS) with user and quarter fixed effects,  and . This allows us to estimate the
effects of genAI by comparing how output changes with changes in AI adoption within the same
user, keeping constant user characteristics that do not change over time, while also controlling for
secular changes that affect all users in a given quarter.

Our main variable of interest, , measures the estimated share of functions user  produced
by genAI in quarter , that is the average prediction of our genAI classifier for functions in this
quarter. Because detection of genAI requires that we observe functions — which in turn requires
commit activity — we measure AI adoption rates in the quarter before the commits are counted.
In other words, our primary specification uses a one-quarter lagged measure of AI adoption. This
avoids mechanical relations between observed AI adoption and commit-based variables. That is,
we estimate:

 =  −1 +  +  +  (S3)
where  is one of our dependent variables. Finally, to determine the precision of our estimates,

S15
we use standard errors clustered by individual user, allowing for correlations in errors within
individuals.

We estimate these models for two types of dependent variables. The first type measures the
activity rates of users in terms of the number of commits they push in each quarter. We create three
types of commit counts. The first,
all
 , counts all commits by a user in a quarter. The second,
mult

counts commits that make changes to multiple files (scripts) in a project. For these commits, it is
more likely that they need to navigate project-level dependencies, making them in principle more
complex. The third,
imp
 , counts commits that add library imports to a script. Libraries are opensource
software modules written (often) by other developers, which users “import” in their own
scripts to use. These libraries are thought of as building blocks of modern software development
[34]. Presumably, these commits are more likely to change major functionality in a script and are
more substantial.

The second way we study user activity aims to quantify changes in the nature of the code users
produce by tracking the kind of software libraries they import in their scripts. The rationale for
this is that different libraries facilitate different types of functionality, revealing information on the
broad programming domain to which a script belongs. Libraries, and especially combinations of
libraries used by programmers, therefore provide a rough indication of what kind of program a user
works on. If we observe that users start using new libraries or library combinations, we interpret
this as a sign that the user experiments with new types of code. This is in line with prior work that
interprets new library combinations in scripts as a sign of innovation [33].
We study two broad kinds of library usage in user commit histories.
•
all
 : the number of unique libraries that a user adds across all their commits in a given
quarter and
•
entry
 : the number of unique libraries that a user adds in quarter  that had not been used in
any prior quarter by the same user.
To initialize the latter, we drop the first year of observations for each user to assess library usage
that is new-to-the-user. We also generate
all
 and
entry
 , which count commit-level library

combinations (i.e., the sets of libraries added in single commit) rather than individual library use
or entry by a user. Finally, we create variables,
all
 and
entry
 , which count the use of, and entry
S16
into, new library pairs, any pairwise combination of libraries in the commit-level library sets used

to generate the  variables.

Finally, to check the robustness of these results, we test two further changes in how we construct

these library-based variables. First, if genAI adds libraries that are atypical and rarely used (socalled
“AI slop”), this may affect the analysis of new-to-the-user entries. To mitigate against this, we

rerun all analyses using only the 5,000 most commonly used libraries. Second, not all libraries will

radically change the domain of code on which a user works. Therefore, we also test what happens

if we use the aggregate, coarsened library categories instead of the libraries themselves, described

in Section S5. This yields the following set of dependent variables:

• 5,000 most common libraries only:

– libraries:
all,5k
 ,
entry,5k
 ;

– library combinations:
all,5k
 ,
entry,5k
 ;

– library pairs:
all,5k
 ,
entry,5k

• Coarsened library categories:

– categories:
all,cat
 ,
entry,cat
 ;

– category combinations:
all,cat
 ,
entry,cat
 ;

all,cat
 ,
entry,cat
 .

– category pairs:

We then proceed by log-transforming each of these dependent variables. To avoid log(0) issues,

we increment each count by 1 unit before taking logs. We then estimate the following models:

log(
type
 + 1) =
type
 −1 +  +  + ,

where
type
 stands for one of the various counts defined above for user  in quarter .  denotes
user fixed effects,  quarter fixed effects.  is the average estimated AI usage rate across

commits by individual  in quarter , as defined in eq. (S2). As before, we lag this variable to

avoid that the commit-based dependent variables are by construction related to our variable of

interest. The resulting parameter estimates ˆ

type
 can be interpreted as semi-elasticities. That is

S17
Commits Library Use Library Entry
All Multi-file Imports Combos Combos-5k Combos-cat Libs. Combos Combos-5k Combos-cat Libs.
(log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1)
(1) (2) (3) (4) (5) (6) (7) (8) (9) (10) (11)

AI Use 0.122*
(0.048)

0.057
(0.033)
0.045
(0.041)
User FE x x x x x x x x x x x
Quarter FE x x x x x x x x x x x

0.071*
(0.032)

0.074*
(0.032)

0.100*
(0.040)

0.093*
(0.039)

0.082*
(0.036)

0.118*
(0.049)

0.093*
(0.040)

0.082*
(0.039)

Obs. 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428
S.E. Cluster User User User User User User User User User User User

2 0.636 0.621 0.610 0.606 0.604 0.595 0.586 0.596 0.593 0.534 0.497

Table S7: Estimated effects of AI usage rate on commit activity, library usage, and library entry.
Stars denote significance levels: ***  < 0.001, **  < 0.01, *  < 0.05. Standard errors clustered

by user are reported in the parentheses.

type
 changes when adoption rates go from 0

they approximately describe by which percentage

to 100%. The results are presented as a figure in the article, and here, as a regression table: Table S7.

S4.2 Placebo tests

One potential concern is that our estimates are confounded by an omitted variable. For instance,

if our AI detection model systematically miss-classifies code by users that differ in their coding

output, this would confound our estimates. To analyze this, we perform a placebo test: we estimate

the effect of user’s —detected— AI usage rates before the introduction of genAI tools. That is, we

rerun our analyzes in a sample that only contains quarters before the year in which co-pilot was

launched, i.e., before 2022. In this period, the detected AI usage shares do not carry any information

on how much users rely on genAI. However, the imprecisely estimated point estimates show that

the statistical power of these placebo tests is not very strong.

Results are reported in Tab. S8. Unlike our results for the entire period, we now find no evidence

that (erroneously) detected AI usage is statistically significantly associated with higher levels of

activity or experimentation: p-values of our AI use range from 0.11 to 0.93. The panels of Fig. S3

similarly shows that there are no salient differences across experience categories in measured AI

use before the introduction of genAI.

S18
Commits Library Use Library Entry
All Multi-file Imports Combos Combos-5k Combos-cat Libs. Combos Combos-5k Combos-cat Libs.
(log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1)
(1) (2) (3) (4) (5) (6) (7) (8) (9) (10) (11)

AI Use 0.136
(0.085)

-0.005
(0.055)
-0.052
(0.070)
User FE x x x x x x x x x x x
Quarter FE x x x x x x x x x x x

0.008
(0.050)

0.004
(0.051)

0.030
(0.064)

0.027
(0.063)

0.015
(0.058)

0.015
(0.080)

0.027
(0.064)

0.017
(0.063)

Obs. 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428
S.E. type User User User User User User User User User User User

2 0.703 0.681 0.675 0.666 0.664 0.651 0.647 0.657 0.653 0.600 0.570

Table S8: Placebo tests of main regressions. Subsetting our dataset to pre-2022 activity where

we expect no AI use, we find no significant relationships between detected AI use and developer
behavior. Stars denote significance levels: ***  < 0.001, **  < 0.01, *  < 0.05. Standard errors

clustered by user are reported in the parentheses.

S4.3 Heterogeneous effects by user experience

To test whether the effects of AI adoption differ across programmer experience levels, we extend

the baseline specification by including an interaction term between AI usage and experience. We

proxy for experience using a developer’s tenure on GitHub, measured as the number of years

since they registered. We classify users with 6 or more years of activity on GitHub as experienced

programmers, and those with less than 6 years as less experienced.

We estimate the following model:

 =  −1+ 1(Experience ≥ 6)+×

−1 × 1(Experience ≥ 6)

+++,

(S4)

where 1(Experience ≥ 6) is an indicator variable equal to 1 if user  has 6 or more years of

activity on GitHub. The coefficient  captures the effect of AI adoption for less experienced users

(the reference category), while  + ×  represents the total effect for experienced users. The

interaction coefficient ×  therefore directly tests whether the productivity and experimentation

effects of genAI differ significantly between experience groups. As before, we estimate these models

using OLS with user and quarter fixed effects, clustering standard errors at the user level. Results

are presented in Tab. S9 and visualized in Figure 3D of the main text.

S19
Commits Library Use Library Entry
All Multi-file Imports Combos Combos-5k Combos-cat Libs. Combos Combos-5k Combos-cat Libs.
(log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1) (log+1)
(1) (2) (3) (4) (5) (6) (7) (8) (9) (10) (11)

High Experience -0.027

-0.023
(0.030)
-0.026
(0.036)
AI Use 0.020

-0.028
(0.028)

-0.016
(0.029)

-0.030
(0.036)

-0.029
(0.035)

-0.022
(0.032)

-0.024
(0.043)

-0.035
(0.036)

-0.035
(0.035)

(0.044)

-0.034
(0.043)
-0.052
(0.055)
High Experience
× AI Use
0.189*
(0.086)
0.188***
(0.055)
0.171**
(0.056)
0.187**
(0.071)
0.179**
(0.069)
0.166**
(0.063)
0.211*
(0.086)
0.196**
(0.069)
0.186**
(0.068)
0.169**
(0.059)
0.179*
(0.073)
User FE x x x x x x x x x x x
Quarter FE x x x x x x x x x x x

-0.030
(0.040)

-0.018
(0.041)

-0.001
(0.051)

-0.004
(0.051)

-0.008
(0.046)

0.004
(0.064)

-0.013
(0.051)

-0.018
(0.050)

(0.064)

Observations 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428 123,428
S.E. type User User User User User User User User User User User

2 0.636 0.621 0.610 0.606 0.605 0.595 0.586 0.597 0.593 0.534 0.497

Table S9: Estimated effects of AI usage rate by high vs low experience users on commit activity,
library usage, and library entry. Stars denote significance levels: ***  < 0.001, **  < 0.01, *
 < 0.05. Standard errors clustered by user are reported in the parentheses.

S4.4 AI adoption and user demographics

Next, we estimate how AI adoption rates themselves differ by experience and gender, focusing on

US-based users. We proxy experience as the number of years since a user’s first recorded activity on

GitHub. Because our data starts in 2011, this experience is right-censored. The longest experience

category therefore contains individuals with the stated number of years of experience or more. Next,

we regress adoption rates in 2024 on a set of dummies that encode the user’s years of experience. We

calculate robust (HC1) standard errors. Point estimates with their confidence intervals are plotted

in Fig. 3, further details are provided in Table S10.

Gender

To estimate usage rates by gender, we first infer a user’s gender using Gender-Guesser https:

//pypi.org/project/gender-guesser/, a dictionary-based method to infer a user’s gender

based on their first name and country (here, the US). As a consequence, this gender may not

accurately reflect the gender the user identifies with. The accuracy of name-based gender inference

is known to vary across nationalities [57], though this is limited to some extent by our focus on

US-based developers and in general the accuracy of these methods is high when checked against

ground-truth (95%+) [58].

Gender-Guesser returns five gender categories (“male”, “mostly male”, “andy”[androgenous],

S20
Panel Panel

Exp 2 -0.017
(0.013)

Exp 10 -0.075***
(0.013)

Exp 4 -0.026*
(0.013)

Exp 12 -0.083***
(0.014)

Exp 6 -0.052***
(0.013)

Exp 14 -0.099***
(0.014)

Exp 8 -0.066***
(0.013)

Intercept 0.371***
(0.012)

Observations: 27,369

: 0.008 S.E. Clustered by: User

Table S10: Effect of Experience on AI Share. Standard errors clustered at the user level. Significance
levels: ***  <0.001, **  <0.01, *  <0.05.

“mostly female” and “female”), indicating the statistical confidence of the classification. Names
outside the method’s training data or with too few examples are classified as unknown. Applying
the method to the US-based developers active in 2024, we find a male-dominated population (see
Tab. S11). The ratio of approximately 10:1 men to women on GitHub aligns closely with estimates
from previous work on gender and participation in OSS using name-based inference [59] and
self-reported gender identity [60].

Inferred Gender Count
“unknown” 18,809
“male” 9,531
“mostly male” 1,001
“female” 983
“andy” 361
“mostly female” 204

Table S11: Distribution of US GitHub users across inferred genders in 2024.

In our primary analysis, we only consider “male” and “female” identified users, mapping the
other cases to “unknown”. We carry out a similar regression analysis to the study of tenure and
AI adoption, replacing the experience dummies by a gender dummy. Point estimates with their
confidence intervals are plotted in Fig. 3, estimates are provided in Table S12. Repeating our
analysis including the less certain gender identifications (“mostly male” and “mostly female” as

S21
male and female, respectively), we find similar results.

AI Share (2024)
(1)
Male -0.004
(0.013)
Unknown 0.009
(0.013)
Intercept (Female) 0.431***
(0.012)
Observations 23,292
S.E. Clustered Robust

2 0.000
Table S12: Relationship between user Gender and AI Share in 2024, US-based developers active
in 2024. Robust standard errors. Significance levels: ***  <0.001, **  <0.01, *  <0.05.

S4.5 Measurement error

The main variable of interest in our study is a user’s AI adoption rate, defined as the (latent)
likelihood that a user uses genAI to program. To estimate this likelihood we use the average score
from our AI-detection algorithm across all functions produced by a user in each given quarter.
The more functions a user commits, the less noisy this estimate will be. That is, the precision of
the estimate of AI adoption rates will depend on the number of functions a user produces in each
quarter. However, in general, AI adoption rates will be measured with some error.
Measurement error is known to lead to attenuation bias, which typically biases the estimated
effect of a variable towards zero. To see this, we introduce the following notation:

• ∗
: real AI usage rate of a user  in quarter , with variance
∗
;
•  = ∗
 + : observed (noisy) estimate of ∗
, with variance
; and
• : error term that is independently distributed from ∗
, with mean zero and variance

.

In the paper, we estimate regression models of the form:
S22
AI Share (2024)
(1)

Male -0.005

(0.011)

Unknown 0.004

(0.010)

Intercept (Female) 0.415***
(0.010)

Observations 32,386
S.E. Type Robust

2 0.000

Table S13: Relationship between user Gender and AI Share in 2024, US-based developers active
in 2024, using a less strict gender identification method. User display names classified by our
gender inference tool as “mostly male” and “mostly female” are counted as male and female in this
analysis; in the main analysis of the paper these are classified as unknown. Robust standard errors.
Significance levels: ***  <0.001, **  <0.01, *  <0.05.

 = −1 +  +  +  (S5)

= ∗
−1

+ −1 +  +  + , (S6)

where  is one of the dependent variables we study and  and  are user and quarter fixed

effects, respectively. The relation in this equation between the true effect of AI, , and the estimated

effect, ˆ, of the observable, but mismeasured variable, , is (e.g., [61]:

ˆ =

1 −

 !

 (S7)

Note that due to the assumed statistical independence between AI adoption rates and measure22=
1 −

∗+

ment errors, the attenuation factor, 1 −

, always lies between 0 and 1, such that

the estimated effects are biased toward zero. Moreover, this term tends to 1 as measurement error

becomes smaller. Consequently,
 → 0 ⇒ ˆ → : the smaller the measurement error, the closer

the estimated effect will be to the true effect.

S23
Although the amount of measurement error is unknown, we can create different versions of

 across which measurement error varies in a known way. To do so, we create variants of

that are based on moving averages. In particular, we average a user’s detected genAI probability

over a fixed number of functions, :

+
∑︁
(/2)−1

 =

  ()

, (S8)

=−  (/2)

where   ()

is the estimated probability that function  () produced by user  with temporal

order  was AI generated. If the window over which functions need to be collected stretches across

more than 184 days (the maximum number of days in two consecutive quarters in our data), we risk

that the underlying ∗
 changes too much, and we drop the observation.

Next, for each user–quarter combination we find the two points 1 and 2 closest to the midpoint

of a given quarter and linearly interpolate between
and

to arrive at an estimate of the

user’s AI adoption rate in that quarter. To avoid interpolations across too long time periods, we drop

user-quarter observation whenever two observations are over 184 days apart. Using this procedure,

we produce the following variables: 4
, 8
, 16
 and 32
.

Assuming observations are identically and independently distributed (IID), the measurement

error variance in each of these variables will equal 1

, where

is the variance of the measurement

1 −

∗+

error in a single function. This means that for any : ˆ =

. Consequently,

attenuation bias should rise with 1/ approaching a linear relation as  grows large .

To test this, we rerun our baseline regression model with each of the variants
 separately,

leading to four different estimates, ˆ

 . Because the number of observations for which we are able

 drops as  rises, we restrict the sample to observations where
 is nonmissing

to calculate ˆ

for all  ∈ {4, 8, 16, 32}. In Fig. S6, we plot these estimates, together with their 95% confidence

intervals, against 1/ for each dependent variable.

Across all models, as measurement error falls, effect estimates rise. Measurement errors are

therefore likely to lead to conservative estimates. Moreover, at very low levels of measurement

error, estimated effects on commit volumes are much closer to those reported in RCTs than our

baseline estimates.

S24
Slope: -1.39
All Commits (log)

Slope: -0.958
Multi-file (log)

Slope: -1.28
Imports (log)

0.0
0.2
0.4
0.6
0.8
1.0

Slope: -1.85
Combos
(Top 5k) (log)

Slope: -1.58
Combos
(Groups) (log)

Slope: -2.21
Indiv.
Libs. (log)

Slope: -1.89
Combos (log)

0.0
0.2
0.4
0.6
0.8
1.0

Estimate of AI effect

Slope: -1.7
Combos
(Top 5k) (log)

Slope: -1.26
Combos
(Groups) (log)

Slope: -1.51
Indiv.
Libs. (log)

0.0
0.2
0.4
0.6
0.8
1.0
Slope: -1.78
Combos (log)

1 / MA window

Figure S6: Effect estimates against measurement error. Within a specific subplot, each marker
indicates the estimated effect of genAI adoption on users’ coding behavior, following our baseline
specification using OLS regressions with user and quarter fixed effects. The row correspond to our
three main measures of user coding behavior: commits, library use, and library entry. Vertical lines
indicate 95% confidence intervals based on standard errors clustered by user.

S25
Commits
All Commits Multi-file Imports
(log +1) (log +1) (log +1)
(1) (2) (3)

AI Use 2nd Quint. 0.065*

0.037
(0.021)
0.050*
(0.021)
AI Use 3rd Quint. 0.109**
(0.034)
0.057**
(0.021)
0.066**
(0.022)
AI Use 4th Quint. 0.084*

(0.033)

0.054*
(0.023)
0.062**
(0.023)
AI Use 5th Quint. 0.093*

(0.036)

0.052*
(0.026)

0.054*
(0.026)

(0.039)

Quarter FE x x x
User FE x x x

Observations 123,428 123,428 123,428
S.E. clustered on User User User

2 0.636 0.621 0.610

Table S14: Investigation of potential nonlinearity in the relationship between AI use and commit
activity. The first (lowest) quintile of AI use serves as reference category. Stars denote significance
levels: ***  < 0.001, **  < 0.01, *  < 0.05.

S4.6 Nonlinearities

In this section, we assess whether the effect of genAI adoption on commit rates is linear or exhibits
nonlinearities, such as threshold effects. To do so, we turn our genAI adoption variable into a

categorical variable that collects observations in the same quintile of AI adoption. Next, we adjust

the regression model of eq. (S3) as follows:

 =
∑︁
=2

1(

 ≤ −1 ≤

) +  +  +  (S9)

where 1(

 ≤ −1 ≤

) is a function that evaluates to 1 if a user’s AI adoption falls between
the lower and upper bounds (

and

) of quintile . The lowest quintile serves as reference

category.

Results are shown in Tab.S14. Although point estimates suggest there may be a threshold above

which benefits of additional AI usage rates flatten off, the precision of these estimates is too low to

S26
warrant strong conclusions.

S5 Coarsening library information into categories

Our analysis of libraries is based on the idea that libraries provide information about the general
programming domains to which code belongs (e.g., visualization, machine learning, front-end
development, DevOps, etc.). A possible objection to this analysis is that genAI may add irrelevant
or redundant libraries to a commit. We mitigate against this by creating coarsened categories of
libraries that collect similar or related libraries. To do so, we study the co-occurrence patterns of
libraries in Python projects, assuming that libraries that often co-occur in a project are likely to be
related in the sense that they are either synergistic or similar in usage.

We first collect all libraries imported in our dataset of commits to Python projects. This yields
over 150k libraries whose frequency roughly follows a scale-free distribution. Somewhat over a
third of libraries feature only once across all projects.

Next, we count how often two libraries co-occur in the same projects. To assess how surprising
these co-occurrences are, we rely on an information-theoretic approach that provides Bayesian
estimates of point-wise mutual information (PMI) [62]. We then construct a library network,
connecting libraries that surprisingly often co-occur, using   > 0 as a threshold. All pairs
meeting this condition are connected by ties whose weight corresponds to the estimated PMI. We
then filter the network for the 5,000 most commonly used libraries. Dropping two isolated nodes,
this yields a network of 4,998 nodes connected by 186,203 edges (see Fig. S7).

Finally, we run a Louvain community detection algorithm to identify library communities in this
weighted graph. We obtain 124 communities, which can be further aggregated into 19 higher-level
communities. From these communities, we derive alternative measures of library use, combination,
and entry by users. For example, in one operationalization, we count how often a user combines a
new pair of library communities in a quarter. In Table S15, we list representative libraries for each
of these high-level communities. To help interpret these lists, we generate descriptions for each
community by feeding the complete list of libraries to Gemini 2.5, using the following prompt:

S27
Figure S7: Library network with communities detected by a Louvain algorithm. Colors mark the
top 10 of the 124 different low-level communities, with descriptions generated by Gemini 2.5.
Edges are not drawn to avoid cluttering the graph.

S28
I would like you to generate short descriptions of each of the 19 lists of Python libraries:
“ ” Specifically, for each library lists, I want to list a domain in software development for
which these libraries are typically used. Here are five examples of such domains:
1) User interfaces; 2) Data science and analytics; 3) Web design; 4) Databases; 5) Embedded
systems and IoT.

Be sure to keep the descriptions short. Also, ensure that no two descriptions are too similar
so that is easy to understand the differences between categories. Finally, do not concatenate
two different types of domains by adding “or” but rather try to generalize across them or, if
that is too hard, pick the most important one.

The Python libraries are separated by ’,’. Lists are enclosed in ’[]’ and the next list is always
on the next line.

ID # libs description / representative libraries

1 923 System & Operating System Utilities: Libraries focusing on interacting with the operating
system, file system, process management, and core interpreter functions.
os, sys, re, subprocess, io, tempfile, shutil, contextlib, inspect, threading

2 903 Scientific Computing, AI & Machine Learning: Core numerical computation, deep learning
frameworks (PyTorch, TensorFlow), and utilities for research and data analysis.
torch, functools, argparse, math, random, tensorflow, transformers, PIL, tqdm, absl
3 831 General Application Development & Testing: Tools for code quality, rigorous software testing
(pytest, unittest), asynchronous programming, and configuration.
typing, future , pytest, unittest, logging, json, collections, dataclasses, tests, homeassistant
4 730 Data Science, Statistics, and Visualization: Foundational libraries for complex data manipulation,
statistical modeling, data visualization (matplotlib, seaborn), and scientific research.
numpy, warnings, pandas, copy, itertools, matplotlib, scipy, ray, pickle, sklearn
5 319 Web Scraping, Content & Desktop UI: Tools for making HTTP requests, parsing HTML,
developing desktop user interfaces (tkinter), and handling multimedia/documents.
requests, csv, streamlit, bs4, tkinter, sqlite3, unicodedata, html, odoo, lxml
6 273 Enterprise Web & Backend Development: Frameworks like Django for large-scale web
applications, REST APIs, time/date handling, and authentication.
datetime, django, decimal, common, rest framework, dateutil, pytz, sentry, core, calendar

S29
ID # libs description / representative libraries (cont.)

7 262 Data Workflow & Web Service Backend: Frameworks for defining and scheduling data
pipelines (Airflow), building web APIs (Flask), and interacting with various database backends
(SQLAlchemy).

airflow, sqlalchemy, flask, app, config, werkzeug, superset, galaxy, lib, pymongo
8 211 Tooling, Packaging, and Documentation: Utilities for code parsing (ast), dependency management
(packaging), configuration file handling (toml, yaml), and generating documentation
(Sphinx, Jinja2).

pathlib, yaml, packaging, ast, pygments, jinja2, sphinx, tornado, docutils, mypy
9 153 Networking, Asynchronous, and Blockchain: Libraries for network programming (Twisted),
cryptographic utilities, and tools related to distributed systems and blockchain technologies.
mock, attr, twisted, jsonschema, synapse, web3, overrides, zope, eth utils, toolz
10 122 Embedded Systems and IoT: Libraries designed for running on microcontrollers and singleboard
computers (MicroPython, RPi), handling low-level hardware I/O.
time, gc, array, board, secrets, micropython, digitalio, machine, ujson, busio
11 92 Computer-Aided Design (CAD) and GUI: Tools for geometric modeling (FreeCAD, Part),
computer graphics, and building advanced, cross-platform graphical user interfaces (PyQt5).
PyQt5, FreeCAD, PySide, FreeCADGui, PySide2, mantid, PySide6, PyQt6, angr, gnuradio
12 59 Cloud and Infrastructure Automation: Libraries for interacting with major cloud providers
(Azure, OCI), building command-line interfaces (knack), and infrastructure testing.
azure, msrest, oci, devtools testutils, knack, msrestazure, jmespath, litex, migen, c7n
13 48 High-Energy Physics & Scientific Simulation: Specialized frameworks (CMSSW, ROOT)
used in fields like particle physics for event simulation, data processing, and analysis.
FWCore, Configuration, ROOT, Geometry, RecoTracker, DQMServices, PhysicsTools, DQM, L1Trigger, RecoMuon
14 32 Scientific Data Analysis & Crystallography: Tools focused on processing and visualizing
scientific data, particularly within crystallography, materials science (cctbx), and image analysis
(dxtbx).

wx, libtbx, watchdog, dials, iotbx, scitbx, colors, mooseutils, cctbx, gui
15 18 Natural Language Processing (NLP) & ML Tasks: Highly specific wrappers and scripts for
common NLP and deep learning tasks like question answering, summarization, and translation.
tf keras, run translation, run qa, run ner, run mlm, run clm, run swag, run summarization, run image classification,
run generation

16 6 Version Control and Git Workflow: Scripts and utilities dedicated to managing Git repositories,
handling pull requests, and automating branch merging processes.

S30
ID # libs description / representative libraries (cont.)

gitutils, trymerge, github utils, label utils, trymerge explainer, test trymerge
17 6 Large-Scale Systems Monitoring and Diagnostics: Libraries for health checks, data collection,
and diagnostic logging, often used for monitoring complex distributed systems.
syscore, sysdata, systems, sysobjects, sysproduction, syslogdiag

18 6 Database Testing and Benchmarking: Tools explicitly designed for creating test harnesses,
scenarios, and running rollbacks to validate the behavior of database systems (WiredTiger).
wttest, wiredtiger, wtscenario, wtdataset, suite subprocess, test rollback to stable01
19 4 Torch/ML Internal Development & Testing: Internal testing and utility modules for the PyTorch
ecosystem, focusing on deep learning performance, dynamic shapes, and core framework
stability.

test torchinductor, test torchinductor dynamic shapes, test cpu repro, test aot inductor utils
Table S15: High level library communities. Labels are generated by Gemini 2.5, based on the libraries that belong to
each community. Table contains 19 high-level communities, as well as a list of the 10 most common libraries for each
community. The primary statistical analyses in the paper are based on the 124 low-level communities.

S6 Estimating the total wage sum related to programming tasks

in the US

Estimating how much the US economy spends on programming tasks is not trivial. On the one
hand, although the US Bureau of Labor Statistics’ (BLS) Standard Occupation Classification (SOC)
lists programming-related occupations, such as Computer programmers and Software developers,
these jobs entail more than just coding tasks. On the other hand, workers in a wide range of other
occupations may not focus on programming but still carry out substantial programming tasks, from
Online merchants to Statisticians. To estimate how much time workers in each of the almost 900
occupations in the SOC classification spend on programming tasks, we rely on data from the Occupational
Information Network (O*NET). Next, we combine this estimate with information from
the BLS’ Occupational Employment and Wage Statistics (OEWS) and the American Community
Survey (ACS) on employment and wages in these occupations to arrive at an estimate of the overall
wage sum in the US that is associated with programming tasks. We link these data sources at the

S31
most detailed, 6-digit, level of the SOC classification.

O*NET is the primary data source for occupational information in the US. It conducts surveys
and expert analysis of occupations to determine a variety of characteristics of jobs [63]. Here, we
mainly use the information O*NET contains on the tasks that occupations require. We focus on
the Task Ratings file of O*NET 29.2, released in February 2025, which lists around 20 tasks for
each occupation, amounting to about 17k distinct tasks. For each task, this file lists how frequently
workers in the occupation perform the task and how important it is in their job. The frequency
information is encoded in a seven-item variable group that provides information on which percentage
of workers in the occupation perform the task with a given frequency, ranging from 1, “yearly or
less,” to 7, “hourly or more.” For example, 34.85% of Online Merchants perform the task Receive
and process payments from customers, using electronic transaction services “daily” (level 5), and
23.91% Calculate revenue, sales, and expenses, using financial accounting or spreadsheet software
“more than weekly” (level 4).

To convert these frequencies into estimates of the share of time that workers in a given occupation
spend on each task, we explore two approaches. In the first (“distributive”) approach, we try to
make reasonable assumptions about how much time a worker spends on tasks in a given frequency
category. We list these assumptions in the third column of Table S16 below. Next, we assume that
workers distribute the time allotted to each frequency category and weight this by the percentage
of responders of the tasks in the category. For example, according to Table S16 tasks performed
“several times daily” (level 6) are assigned a weight of 0.25. That is, we assume that tasks with
level 6, taken all such tasks together, amount to 25% of the working time in an occupation. If the
occupation contains three tasks at frequency level 6 with weights %, %, and %, then these three
tasks together, with weights
++
,

++
, and
++
, compose 25% of total working time. We then
multiply these weights with their distributive weight (in this case, 0.25) and repeat this process
across all 7 frequency categories. This yields the final weights for each of an occupation’s tasks.

In the second (“relevance”) approach, we instead interpret the frequency information for each
task as weights that directly express the amount of time workers spend on this task. To do so,
we choose a weight for each of the seven frequency categories. These weights are listed in the
fourth column of Table S16. Each weight is multiplied by the worker share information. Next, these
products are summed and normalized such that they add up to one within each occupation.

S32
frequency scale category description weights (distributive) weights (relevance)
1 Yearly or less 0 0.5
2 More than yearly 0.02 1
3 More than monthly 0.05 4
4 More than weekly 0.08 48
5 Daily 0.1 240
6 Several times daily 0.25 480
7 Hourly or more 0.50 1920
Table S16: Scales, description, and weights under the two approaches to turn frequency categories
in the Task Ratings O*NET file into duration shares.

Finally, we need to determine how much of the time spent on each task is dedicated to programming.
To estimate this, we rely on an open source large language model, Llama 3.3. We provide the
model with three different prompts — listed a the end of this section — to arrive at three different
estimates of the programming intensity of each task. Table S18 provides examples of tasks and the
extent to which they require programming using all three prompts.

Figure S8 provides scatter plots that compare our different estimates of the amount of time spent
on programming tasks in each occupation to the importance of programming skills (not tasks) for
the occupation as reported in O*NET. The graph shows that all approaches yield estimates that
correlate strongly with the importance of programming skill requirements, with correlations ranging
between .76 and .80. In general, the correlation is highest for the third, most detailed, prompt.

To arrive at the total wage sum related to programming tasks in the US in 2023, we use two
different datasets. The first uses information taken from the BLS on employment and wages:

Programming Wage Sum = ×

∑︁

annual wage
 × employment
 ×
 ∑︁
∈Θ
working time, × programming share,

, (S10)

where annual wage

is the average annual wage in occupation  reported by the BLS, employment

the number of employees in occupation  according to the BLS, share time, the estimated
share of time that workers in occupation  spend on task  based on O*NET information,
programming share,  the LLM’s estimated share of task  spent on programming, and  = 1.449
the average wage-to-compensation ratio in the US according to the BLS [64, 65] to account for

S33
distributive

relevance

Figure S8: Programming tasks versus programming skills. Scatter plots of programming shares
by occupation based on the three different prompts and the distributive (top row) or the relevance
(bottom row) approach of turning frequencies into time shares against the importance of programming
skills as reported in O*NET.

wage-related costs borne by the employer.

The second dataset is the 2023 American Community Survey (ACS). The ACS contains a 1%
weighted random sample of individuals in the US. We aggregate these data to the occupation level,
using the sampling weights as follows:

Programming Wage Sum = ×

∑︁

 × annual wage

 ∑︁
∈Θ()

. (S11)

working time,() × programming share,()

where
is the frequency weight of individual  in the ACS, annual wage

the annual salary
listed for individual  and () individual ’s occupation.

Unlike the BLS data, the ACS samples individuals of all ages and employment statuses (including
self-employed and part-time workers). We follow prior literature [66] to adjust top-coded
annual wages and filter individuals to the active working age population. Occupations in the ACS

S34
are sometimes slightly more aggregated than in O*NET: about 110 SOC codes in ACS correspond
to multiple occupation titles in O*NET. In these cases, we average the O*NET scores across the
disaggregated SOC occupations that are associated with the (more aggregate) ACS occupation.
distributive relevance
BLS ACS BLS ACS

prompt 1 928.33 ± 0.10 1063.41 ± 0.08 937.46 ± 0.09 1080.72 ± 0.07
prompt 2 637.28 ± 0.06 764.63 ± 0.06 641.04 ± 0.06 772.12 ± 0.06
prompt 3 677.91 ± 0.09 760.64 ± 0.08 674.32 ± 0.08 763.45 ± 0.07

Table S17: Estimated wage sum for programming tasks in the US in 2023 in Billions of USD.
Ranges (±) reflect 95% simulated confidence intervals based on the uncertainty bands provided
by O*NET for task frequencies.

Table S17 presents estimated wage sums for programming tasks in the US based on the two
different samples, the three different prompts and the two different approaches to turn frequency into
time-share information. Wage sums range from 637B-1,063B USD. Note that ACS based estimates
always exceed BLS based results. This is because BLS only counts full-time employees and omits
self-employed individuals, while the ACS samples individuals regardless of their employment
status. Wage sums based on the first prompt are generally higher than those based on the other two
prompts, whose estimates are very close to one another. This difference is mainly driven by tasks
that are only marginally related to programming, receiving a score of 1 or 2 out of 5. Overall, the
wage sums reported in Table S17 imply that 2 ∼ 4% of US GDP is spent on remunerating pure
programming work.

Prompts to estimate the programming share of tasks. We supply three different prompts to
a Llama 3.3 model to estimate which percentage of their time workers dedicate to programming
tasks. The first prompt returns a score on a scale that ranges from 1 to 5, where 1 signals that 0%
of working time is dedicated to programming and 5 means that almost all working time is used for
programming. The detailed prompt is:

Analyze the relationship between a specific job task and the skill of computer programming.
**Job Role:** “ ”

**Task Description:** “ ”

S35
**Instructions:**

1. Consider the definition of ”computer programming” as the act of writing, modifying,
testing, debugging, or maintaining code or scripts (e.g., using languages like Python, Java,
C++, SQL, shell scripts, PowerShell, etc.).
2. Evaluate how much of the *specific task described above* involves performing computer
programming activities. Do not evaluate the entire job role, only the task provided.
3. Provide *only* a single numerical score from 1 to 5 based on the scale below. Do not add
any explanation or text other than the score itself.
**Scoring Scale:**
* **1:** This task is not related to computer programming at all.
* **3:** Performing this task involves spending around half of the time on computer programming
activities.

* **5:** This task is very related to computer programming, and performing it involves
spending almost 90% of the time on computer programming activities.
**Score:**

The second prompt is a more detailed version of the first one. For each task in each job, it
returns a score on a scale that ranges from 0 to 5 where 0 stands for 0% of working time dedicated
to programming and 5 for almost all time dedicated to programming. The percentage range of each
index is given in the prompt. The detailed prompt is:

Analyze the relationship between a specific job task and the skill of computer programming.
**Job Role:** “ ”
**Task Description:** “ ”
**Instructions:**

1. Consider the definition of ”computer programming” as the act of writing, modifying,
testing, debugging, or maintaining code or scripts (e.g., using languages like Python, Java,
C++, SQL, shell scripts, PowerShell, etc.).
2. Evaluate how much of the *specific task described above* involves performing computer
programming activities. Do not evaluate the entire job role, only the task provided.

S36
3. Provide *only* a single numerical score from 0 to 5 based on the scale below. Do not add
any explanation or text other than the score itself.
**Scoring Scale (0-5):**

* **0:** **None.** The task involves absolutely no computer programming activities.
*(Estimated programming proportion: 0%)*

* **1:** **Minimal / Trace.** Programming is present but extremely limited or incidental,
a negligible part of the task. *(Estimated programming proportion: 1% - 10%)*
* **2:** **Minor / Some.** Programming is a recognizable but small part of the task,
clearly secondary to other activities. *(Estimated programming proportion: 11% - 25%)*
* **3:** **Moderate.** Programming constitutes a significant portion, but typically less
than or roughly equal to other activities within the task. *(Estimated programming proportion:
26% - 50%)*

* **4:** **Substantial / Major.** Programming is a primary activity, taking up a clear
majority of the effort for the task. *(Estimated programming proportion: 51% - 75%)*
* **5:** **Main.** Programming is the main activity, taking up all or almost all of the
effort for the task. *(Estimated programming proportion: 76% - 10%)*
**Score:**

The third prompt is even more detailed than the first two. For each task in each job, it returns
a score on a scale that ranges from 0 to 100 that indicates the programming related working time
percentage. Several examples are provided to anchor the scale. The detailed prompt is:

**Prompt for Llama 3:**
**Context:**

You are an AI assistant tasked with analyzing job roles and specific tasks within those roles
to estimate the proportion of time dedicated to programming activities. I will provide you
with a job title and a description of a single task performed within that job.
**Your Goal:**

Based on the provided job title and task description, estimate the approximate percentage
of time that would be spent **actively writing, testing, debugging, or deploying code** for

S37
this specific task. Your output should be **only the numerical percentage value**. Focus on
inferring the nature of the work from the overall description, rather than relying solely on
specific keywords.
**Input:**
* **Job Title:** “
* **Task Description:** “

**Instructions for Your Analysis (Internal Thought Process - Do Not Include in Output):**
1. **Holistic Task Understanding in Job Context:**

* Read the ‘Task Description‘ thoroughly. Instead of just looking for keywords like ”develop”
or ”code,” try to understand the overall objective and the types of activities implicitly required
to achieve it, considering the typical responsibilities of the given ‘Job Title‘.
* For instance, a task described as ”resolve customer-reported performance bottlenecks in the
data processing pipeline” implies deep investigation, potentially code profiling, optimization,
and testing, even if the word ”coding” isn’t explicitly used.
2. **Infer Programming-Related Activities:**

* Based on your holistic understanding, determine what proportion of the task likely involves
direct engagement with programming activities (e.g., designing algorithms that will be
coded, writing new code, modifying existing code, scripting, debugging complex systems,
implementing tests, or managing code deployment).

* Consider the full software development lifecycle if implied by the task.
3. **Consider Implied Non-Programming Activities:**

* Also, identify parts of the task that, based on its nature, would likely involve significant
non-programming activities. This could include extensive research before any coding can
begin, detailed planning and architecting, writing documentation, attending meetings for
coordination, user interviews, data gathering and analysis (if not directly scripting it), or
system monitoring and analysis that doesn’t immediately lead to code changes.
4. **Estimate the Percentage based on Inferred Effort:**

* Determine a single numerical percentage representing your best estimate of the time spent
on direct programming activities for this *specific task*, based on the inferred balance of

S38
efforts.
**Output Requirement:**

* Return **ONLY the numerical percentage value**. For example, if you estimate 30%,
output only ‘30‘. Do not include the ’%’ symbol or any other explanatory text.
**Examples of Task Analysis (Illustrative - For your understanding of the analysis process
only, not the output format for the actual task. Note how the reasoning infers activities):**
* **Example 1 (Low Programming):**
* **Job Title (Example):** Software Engineer

* **Task Description (Example):** ”Collaborate with the product team to define specifications
for a new user authentication module.”

* **Internal Estimation Logic (Example):** The description emphasizes collaboration (”collaborate”)
and definition of requirements (”define specifications”). This strongly suggests activities
like discussion, documentation, and planning, which are primarily pre-coding. *This
specific task* is about laying the groundwork. Estimated programming time for *this specific
task*: 10%.

* **Example 2 (Mid-Range Programming):**
* **Job Title (Example):** Data Scientist

* **Task Description (Example):** ”Investigate anomalies in sales data and present findings
to the marketing department.”

* **Internal Estimation Logic (Example):** ”Investigate anomalies” might involve some
scripting for data extraction and initial analysis. However, ”present findings” implies data interpretation,
visualization, report preparation, and communication. Estimated programming
time for *this specific task*: 35%.
* **Example 3 (Mid-Range Programming):**
* **Job Title (Example):** DevOps Engineer

* **Task Description (Example):** ”Oversee the migration of our primary application
servers to a new cloud provider, ensuring minimal downtime and performance continuity.”
* **Internal Estimation Logic (Example):** ”Oversee the migration” involves planning and
coordination. While automation scripts (programming) will be part of ensuring ”minimal

S39
downtime and performance continuity,” a significant portion involves project management
and validation. Estimated programming time for *this specific task*: 40%.
* **Example 4 (Low Programming):**
* **Job Title (Example):** UI/UX Designer

* **Task Description (Example):** ”Create interactive prototypes for the upcoming mobile
application redesign based on user feedback and usability testing results.”
* **Internal Estimation Logic (Example):** Prototyping here focuses on design tools and
user experience demonstration, not general-purpose programming, even if some tools have
coding-like features. Estimated programming time for *this specific task*: 15%.
* **Example 5 (High Programming):**
* **Job Title (Example):** Full Stack Developer

* **Task Description (Example):** ”Refactor the existing monolithic backend service into
a set of microservices to improve scalability and maintainability.”

* **Internal Estimation Logic (Example):** ”Refactor... into a set of microservices” is a
substantial software engineering effort involving deep code analysis, writing significant new
code, and extensive testing. Estimated programming time for *this specific task*: 80%.
* **Example 6 (Very High Programming):** * **Job Title (Example):** Computer Programmers*
**Task Description (Example):** ”Perform or direct revision, repair, or expansion of
existing programs to increase operating efficiency or adapt to new requirements.”
* **Internal Estimation Logic (Example):** This task is the core of what a computer
programmer does. ”Revision, repair, or expansion of existing programs” directly translates
to reading, understanding, modifying, testing, and debugging code. Estimated programming
time for *this specific task*: 95%.
* **Example 7 (Very High Programming):**
* **Job Title (Example):** Computer Programmers

* **Task Description (Example):** ”Write, update, and maintain computer programs or
software packages to handle specific jobs such as tracking inventory, storing or retrieving
data, or controlling other equipment.”

S40
* **Internal Estimation Logic (Example):** ”Write, update, and maintain computer programs”
is unequivocally direct programming work. This involves the full cycle of coding for
specific functionalities. Estimated programming time for *this specific task*: 95%.
* **Example 8 (Very High Programming):**
* **Job Title (Example):** Web Developers

* **Task Description (Example):** ”Write supporting code for Web applications or Web
sites.”

* **Internal Estimation Logic (Example):** ”Write supporting code” is a direct statement of
programming activity within the context of web development (e.g., backend logic, frontend
scripting, API integration). Estimated programming time for *this specific task*: 90%.
* **Example 9 (Very High Programming):**
* **Job Title (Example):** Bioinformatics Technicians

* **Task Description (Example):** ”Write computer programs or scripts to be used in
querying databases.”

* **Internal Estimation Logic (Example):** ”Write computer programs or scripts” for
database querying is a clear programming task, essential for data retrieval and analysis
in bioinformatics. Estimated programming time for *this specific task*: 90%.
* **Example 10 (Very High Programming):**
* **Job Title (Example):** Atmospheric and Space Scientists
* **Task Description (Example):** ”Develop computer programs to collect meteorological
data or to present meteorological information.”

* **Internal Estimation Logic (Example):** ”Develop computer programs” for data collection
or presentation directly points to software development, likely involving data processing,
numerical modeling, or visualization coding. Estimated programming time for *this specific
task*: 85% (allowing for some potential non-coding research or data interpretation elements
within the broader task).
* **Example 11 (Very Low Programming):**
* **Job Title (Example):** Chief Executives

* **Task Description (Example):** ”Appoint department heads or managers and assign or

S41
delegate responsibilities to them.”
* **Internal Estimation Logic (Example):** This task is purely managerial and strategic,
involving decision-making, leadership, and organizational structuring. There is no implied
programming. Estimated programming time for *this specific task*: 0%.
* **Example 12 (Very Low Programming):**
* **Job Title (Example):** Education and Childcare Administrators, Preschool and Daycare
* **Task Description (Example):** ”Teach classes or courses or provide direct care to
children.”

* **Internal Estimation Logic (Example):** This task involves direct pedagogical activities,
caregiving, and interpersonal interaction, with no programming component. Estimated
programming time for *this specific task*: 0%.
* **Example 13 (Very Low Programming):**
* **Job Title (Example):** Food Service Managers
* **Task Description (Example):** ”Test cooked food by tasting and smelling it to ensure
palatability and flavor conformity.”
* **Internal Estimation Logic (Example):** This task involves sensory evaluation and quality
control related to food, entirely non-programming. Estimated programming time for *this
specific task*: 0%.
* **Example 14 (Very Low Programming):**
* **Job Title (Example):** Gambling Managers
* **Task Description (Example):** ”Notify board attendants of table vacancies so that
waiting patrons can play.”

* **Internal Estimation Logic (Example):** This task is operational and communicative,
focusing on managing customer flow and staff coordination within a gambling establishment.
No programming is involved. Estimated programming time for *this specific task*: 0%.
* **Example 15 (Very Low Programming):**
* **Job Title (Example):** Postmasters and Mail Superintendents
* **Task Description (Example):** ”Select and train postmasters and managers of associate
postal units.”

S42
* **Internal Estimation Logic (Example):** This task is focused on human resources,

management, and training, with no direct programming activities. Estimated programming

time for *this specific task*: 0%.

**Now, please analyze the following and provide ONLY the numerical percentage as output,

focusing on an inference from the overall description:**

* **Job Title:** “

* **Task Description:** “

**Begin Analysis and Provide Only the Numerical Percentage. Please only give me the

numerical percentage and do not output any other text.**

Table S18 provides examples of tasks and their scores from the three prompts.

Table S18: Fifteen example tasks and jobs from O*NET with their programming share score and

corresponding percentage provided by Llama 3.3 using three different prompts.

Job Task Prompt 1 Prompt 2 Prompt 3

Robotics Engineers Write algorithms or programming code for ad hoc
robotic applications. 5 (87.5%) 5 (88%) 95 (95%)
Biostatisticians Write program code to analyze data with statistical
analysis software. 5 (87.5%) 5 (88%) 90 (90%)
Computer Systems Engineers/Architects Develop efficient and effective system controllers. 5 (87.5%) 5 (88%) 80 (80%)
Computer and Information Research Scientists Analyze problems to develop solutions involving
computer hardware and software. 4 (62.5%) 4 (63%) 80 (80%)
Financial Quantitative Analysts Devise or apply independent models or tools to
help verify results of analytical systems. 4 (62.5%) 4 (63%) 70 (70%)

Computer Network Architects
Develop or recommend network security measures,
such as firewalls, network security audits,
or automated security probes.
4 (62.5%) 3 (38%) 60 (60%)

Computer Network Architects
Design, build, or operate equipment configuration
prototypes, including network hardware, software,
servers, or server operation systems.
3 (37.5%) 3 (38%) 60 (60%)

Telecommunications Engineering Specialists
Implement system renovation projects in collaboration
with technical staff, engineering consultants,
installers, and vendors.
2 (12.5%) 2 (18%) 40 (40%)

Develop or document reverse logistics management
processes to ensure maximal efficiency of
product recycling, reuse, or final disposal.
2 (12.5%) 2 (18%) 20 (20%)

Logistics Engineers

Bookkeeping, Accounting, and Auditing Clerks Reconcile records of bank transactions. 2 (12.5%) 1 (5.5%) 10 (10%)

Pump Operators, Except Wellhead Pumpers
Record operating data such as products and quantities
pumped, stocks used, gauging results, and
operating times.
2 (12.5%) 1 (5.5%) 5 (5%)

Operating Engineers and Other Construction
Equipment Operators
Locate underground services, such as pipes or
wires, prior to beginning work. 2 (12.5%) 1 (5.5%) 5 (5%)
Administrative Services Managers Set goals and deadlines for the department. 1 (0%) 0 (0%) 0 (0%)

Cement Masons and Concrete Finishers
Spread roofing paper on surface of foundation,
and spread concrete onto roofing paper with
trowel to form terrazzo base.
1 (0%) 0 (0%) 0 (0%)

First-Line Supervisors of Farming, Fishing, and
Forestry Workers

Treat animal illnesses or injuries, following experience
or instructions of veterinarians. 1 (0%) 0 (0%) 0 (0%)

S43
S7 General equilibrium effects

If genAI increases the productivity of programmers, this will not only affect the quantity of code
produced, but also its price. Although a full fledged calibrated general equilibrium model is beyond
the scope of the current paper, in this section we try to put some plausible bounds on such general
equilibrium effects of genAI. To do so, we consider two scenarios. Both scenarios feature a —for
simplicity, linear—standard downward-sloping demand curve. They differ in the assumptions about
the supply curve, representing polar opposite cases: perfectly elastic and perfectly inelastic supply.

Scenario 1: perfectly elastic supply of code
In this scenario, the supply of code is perfectly elastic. That is, programmers supply any quantity of
code at price 1 . For instance, if there were a large pool of identical programmers who can freely
enter or exit the market for code and who all have the same outside option offering a reservation
wage,
∗
, per day, programmers enter (or exit) the market, until the equilibrium price for code,
∗
is such that their earnings  ∗ =
∗
, where  is the volume of code a programmer can write in a
day.

Under such a scenario, illustrated in Fig. S9A, changes in demand will be absorbed by programmers
entering or leaving the coding market without changing the price of code. Productivity effects
of genAI now increase how much code a programmer can produce per day, shifting the supply
curve down. The excess wages will attract additional programmers into the market, increasing the
supply of code while moving down along the demand curve until the new equilibrium price 2 is
reached and incomes again match reservation wages.

S44
loss
A B

Perfectly elastic supply
p

Perfectly inelastic supply
p

S1 S2

gain

gain

p1
p2

p1
p2

�q
�p S1
S2
D

�q
�p

D

q1 q2 q

q1 q2 q

Figure S9: Changes in social surplus due to genAI. Green lines display demand curves, orange
lines supply curves in the price () - quantity () plane. With the introduction of genAI, there is
a shift in supply from 1 to 2. The colored areas represent changes in the social surplus (ΔΣ),
consisting of changes in the producer surplus (ΔΣ) and in the consumer surplus (ΔΣ). Panel A
shows how genAI changes prices and quantities of code in a scenario where the supply of code is
perfectly elastic. Panel B shows the same when the supply of code is perfectly inelastic.
The result is an increase in the consumer surplus, Σ, reflecting two effects: First, the price
of code drops, leading to savings for all original consumers of code (blue rectangle). Second, at
the new price, 2, consumers will demand additional code, some of which will be sold below
the consumer’s willingness-to-pay (purple triangle). At a perfectly elastic supply, the producer
surplus, Σ, is zero, both before and after the arrival of genAI. Changes in the total social surplus,
ΔΣ = ΔΣ + ΔΣ, therefore fully consist of changes in the consumer surplus.
To calculate the value of ΔΣ, we introduce some notation:
• 1: price of a unit of code before introduction of genAI
• 2: price of a unit of code after introduction of genAI
• 1 : quantity of code before introduction of genAI
• 2: quantity of code after introduction of genAI
• 1: number of coders before introduction of genAI
• 2: number of coders after introduction of genAI
S45
Δ
=
2−1
: effect of genAI, the percentage increase in quantity of code due to the
adoption of genAI

∗ =
=

•
∗

: reservation wage satisfying

• 1 = 11: value of code before introduction of genAI

Δ/1
Δ/1

Δ/1
/1

: demand elasticity of code, implying Δ =

The change in social surplus, ΔΣ, equals the area of two colored areas:

ΔΣelas = (1 − 2)
1 + 2
= −Δ
21 + Δ
= −
Δ/1
/1
1 −
Δ/1
/1
Δ
= −
Δ

1 +
Δ

= −

1 +

Note that, except for the demand elasticity, , all parameters in this expression are known.

S7.1 Scenario 2: perfectly inelastic supply of code

In the second scenario, supply of code is perfectly inelastic, yielding a vertical supply curve. This is
a likely short-run scenario, where the labor market has insufficient time to adjust to the productivity
effects of genAI. Under this scenario, the set of programmers in the market is fixed, because it is
hard to move in or out of the coding labor market. As a result, they will supply their labor at any
price the market supports.

With a fixed set of coders, productivity effects of genAI translate one-to-one into an increase
in the equilibrium amount of code supplied to the market, shifting the supply curve of code to the
right. This results in changes in both consumer and producer surplus. Producers of code receive
compensation for the increased volume of code. However, they also bear a cost because they receive
a lower price for their code. In Fig. S9B, this is represented by the two colored rectangles. The
producer surplus is reduced by the area of the blue shape but increased — because of the higher

S46
demand for code at price 2 and producers’ willingness to supply this code at any price —- by the
area of the orange shape. Consequently, the net effect on the producer surplus is ambiguous.

By contrast, consumers unambiguously gain, because the equilibrium price of code falls. As in
Scenario 1, this induces them to consume more code. As before, the increase in consumer surplus
therefore equals the sum of the areas of the blue rectangle and the purple triangle.

Taken changes in consumer and producer surplus together, the net change in social surplus is
unambiguously positive and equal to the areas of the orange rectangle and the purple triangle:

ΔΣinelas = Δ
1 + 2
= Δ 1 +
ΔΔ

Δ
Δ/1
/1
=
Δ

1 +
Δ

= Δ 1 +

= 1

1 +

S7.2 Comparing changes in social surplus

To calculate the changes in social surplus in the two scenarios sketched above, we need an estimate
of , the elasticity of the demand of code. Software code is often tailored to a specific use case and
therefore will typically have few close substitutes. Therefore, we expect demand to be relatively
insensitive to price changes, suggesting inelastic demand:  < −1.

We do not know of any estimates of the elasticity of demand for software code. To get a sense
of its likely magnitude, we can look at other types of intellectual property (IP) that are similarly
high-value, intangible and with few close substitutes: patents and trademarks. For IP protected by
patents [67] estimate an elasticity of −0.3, whereas [68] estimates an elasticity of between −0.25
and −0.40 for IP protected by trademarks. Combining the  = −0.3 estimate for patent-based IP
with the average of our range for the coding-related wage sum in the US of 1 = 787 billion USD
and our baseline estimates for the effect on productivity effect of genAI in the US at the end of 2024
of  =
∗29% − 1 = 3.6% adoption rate, we arrive at the following estimates for the increases in
the social surplus in billions of USD:

S47
∗ 787

1 +

=
0.035
0.3

0.035

= 93.1

elas = −

• Σ

1 +

1 +

= 0.035 ∗ 787

0.035
0.3

inelas = 1

1 −

= 25.9

• Σ

Given this range of possible long-run outcomes, our initial, short-run, estimate of 27.6 billion USD

(using again the average estimate of the wage sum) is relatively conservative.

S48
