---
source: 2025_Question_and_Answer_posts_on_Stack_Overflow.pdf
pages: 29
extractor: pdftext
tokens_raw: 26154
tokens_compressed: 17972
compression: 31%
---

The building blocks of software work

explain coding careers and language popularity

Xiangnan Feng1

, Johannes Wachs2,3,1, Simone Daniotti1,4, and Frank Neffke*1

1Complexity Science Hub, Vienna, Austria
2Corvinus University, Budapest, Hungary

3HUN-REN Centre for Economic and Regional Studies, Budapest, Hungary
4Utrecht University, Utrecht, the Netherlands

arXiv:2504.03581v1 [econ.GN] 4 Apr 2025

April 7, 2025

Abstract
Recent waves of technological transformation have fueled debates about the changing nature of work.
Yet to understand the future of work, we need to know more about what people actually do in their jobs,
going beyond educational credentials or job descriptions. Here we analyze work in the global software
industry using tens of millions of Question and Answer posts on Stack Overflow to create a fine-grained
taxonomy of software tasks, the elementary building blocks of software development work. These tasks
predict salaries and job requirements in real-world job ads. We also observe how individuals learn within
tasks and diversify into new tasks. Tasks that people acquire tend to be related to their old ones, but of
lower value, suggesting that they are easier. An exception is users of Python, an increasingly popular
programming language known for its versatility. Python users enter tasks that tend to be higher-value,
providing an explanation for the language’s growing popularity based on the tasks Python enables its users
to perform. In general, these insights demonstrate the value of task taxonomies extracted at scale from large
datasets: they offer high resolution and near real-time descriptions of changing labor markets. In the case of
software tasks, they map such changes for jobs at the forefront of a digitizing global economy.

Classification: Social Sciences/Economics
Keywords: human capital; tasks; software; economic complexity; networks

1 Introduction

Knowledge of the tasks that workers perform is central to understanding wages, productivity, and overall labor market
dynamics [Acemoglu and Autor, 2011]. Recent work has transformed our ability to do so by using complex network
analysis — moving away from descriptions that rely on years of schooling, credentials, and work experience to the
granular building blocks of human capital: skills and tasks [Anderson, 2017, Alabdulkareem et al., 2018, Hosseinioun
et al., 2025]. These studies focus on jobs, describing them as networks of skills or tasks using data on skill requirements
and task descriptions extracted from large-scale surveys [one, 2025], expert assessments [Commission, 2017], job ads
[Borner et al., 2018] or online freelance platforms[Anderson, 2017, Stephany and Teutloff, 2024]. Yet, job descriptions ¨
tell us something about the nature of vacancies, not of the people who fulfill them. This limits our ability to understand
how workers specialize and learn new things, processes critical to a successful career.
*Correspondence can be sent to neffke@csh.ac.at.

Focusing on the software sector, we propose a new approach that uses data from Stack Overflow (SO), a very large,
online question-answer database. The core insight we leverage is that questions on SO describe coding problems that
programmers encounter in their work. As such, they can be understood as instantiations of software-development jobtasks.
By generalizing these descriptions of specific problems encountered at work, we can construct a taxonomy of
canonical software tasks that is highly granular, flexible and based in data. Moreover, we can use this taxonomy to
describe the human capital endowments of people, not the human capital requirements of jobs. That is, we ask what
programmers do at work, not what they are supposed to do according to their job descriptions. This allows us to analyze
how programmers learn new tasks and what the value of these tasks is. Moreover, programmers can choose from a wide
menu of programming languages and we show that programming languages differ in the tasks they support. However,
the mapping of tasks to programming languages changes over time, as illustrated by the rapid rise of Python as a general
purpose language. Our task network shows that this rise exploits a remarkable strength of Python: it allows programmers
to more quickly transition to the most valuable programming tasks.

As wages and careers have come to depend on how workers specialize [Hosseinioun et al., 2025], interact [Deming,
2017], complement colleagues [Neffke, 2019], and move across places and jobs [Frank et al., 2024], fine-grained taxonomies
of tasks are increasingly valuable. Such taxonomies clarify how workers transition between occupations [del
Rio-Chanona et al., 2021], how skills can substitute for or complement each other [Anderson et al., 2012, Neffke, 2019],
and how occupations evolve over time [Nedelkoska et al., 2021].

In this paper, we focus on jobs in the global software development sector. Software production is a fast-changing
and critical domain of the digital economy [Brynjolfsson and McAfee, 2014, Wachs et al., 2022, Juhasz et al., 2024]. ´
Of the seven largest companies by market capitalization worldwide, three (Microsoft, Alphabet, and Meta) focus almost
exclusively on software, while three others (Nvidia, Apple, and Amazon) derive substantial revenue from it. Demand for
programming skills continues to surge: one in 11 U.S. occupations now requires coding [one, 2025], and software-related
roles such as data scientist, information security analyst, and computer research scientist rank among the fastest-growing

occupations [U.S. Bureau of Labor Statistics, 2025]. As new hardware, programming languages, and specialized libraries
reshape computing, fresh roles (e.g., web development, DevOps, data science, artificial intelligence) keep emerging [Rock,
2019, Papoutsoglou et al., 2019, Hemon et al., 2020]. This changing landscape has sparked intense global competition for
talent, prompting many major economies to designate software development as a strategic priority [Draghi, 2024, Kazim
et al., 2021, Singh, 2024].

However, we currently lack a detailed understanding of the fast-changing human capital that is employed in this
sector. One reason is that databases linking occupations to tasks (e.g., O*NET [one, 2025]) are often curated by human
experts, making them relatively coarse and slow to update. In O*NET, for example, software-related tasks often focus on
broad domains of application (e.g., “geoinformatics” or “biostatistics”), team dynamics (e.g., managing or collaborating
with software engineers), or acquiring software products. Alternative data sources such as job advertisements or resumes
are also challenging because job ads describe job requirements of ideal-type workers, not human capital endowments of
actual workers, resumes can be aspirational, and both often focus on limited geographies. Likewise, platforms for online
freelancing provide insights into how complex skill interdependencies affect wage premiums [Anderson, 2017, Stephany
and Teutloff, 2024], but the extent to which these findings generalize to the broader labor market remains uncertain.

We address these gaps by analyzing millions of posts from SO—the largest question-and-answer forum for programmers
[Anderson et al., 2012]. Each post describes a specific technical challenge and includes tags that indicate the tools,
languages, or concepts involved [Barua et al., 2014]. These challenges reflect real-world coding tasks and users use their
posting histories in part to signal their skills to prospective employers [Xu et al., 2020]. Interpreting tags as a structured,
albeit partial, description of posted questions, we aggregate questions to create a software-task taxonomy by identifying
clusters of frequently co-occurring tags. Using this taxonomy, we examine how software tasks evolve in the labor market.
We find that task value estimates, derived from survey data, significantly predict salaries in real-world job postings.
Notably, wages vary greatly among these tasks, with higher-paying ones concentrated in more specialized or in-demand
fields such as AI and machine learning. We also introduce a notion of task relatedness based on co-occurrence patterns in

users’ posting histories. This measure of relatedness derived from interactions with the SO platform predicts similar cooccurrence
trends in job ads, suggesting that our taxonomy captures a meaningful structure of the software development
landscape.

At the individual user level, we observe two learning patterns. First, developers improve in the tasks they gain

experience in, as measured by community feedback on their posts. Second, developers enter new tasks over their SO
careers, and task relatedness strongly influences these entries: developers are fifteen times more likely to move into tasks
related to ones they already know. At the same time, we find that developers usually add tasks with lower market value,
which are presumably easier to master.

Finally we demonstrate that our fine-grained software task taxonomy sheds light on the evolution of software development
as a whole. We observe that programming languages differ in the number of tasks for which they are used,
following a nested pattern of tasks in programming languages reminiscent of similar patterns observed in ecology [Bascompte
et al., 2003], economic development [Hidalgo and Hausmann, 2009, Tacchella et al., 2012, Mariani et al., 2019]
and skill hierarchies [Hosseinioun et al., 2025]. Accordingly, instead of specialization, where different languages are used
to perform different types of tasks, we observe that tasks have an implicit hierarchy such that the most ubiquitous tasks
can be performed in all languages, whereas rare tasks are only performed by the most versatile ones. A prime example
of the latter is the Python programming language, a popular language that has seen significant growth in recent years
[Economist, 2018]. We show that this growth has been accompanied by changes in the way Python is used. First, Python
has become increasingly versatile. From 2015, the number of tasks in which Python dominates as the preferred language
for most programmers has rapidly grown, rendering Python into one of today’s premier general purpose languages. Second,
Python enables qualitatively different paths for users to learn new tasks. Specifically, unlike users of most other
languages, Python users often branch into more, not less valuable tasks. This observation could help explain Python’s
success, despite its not being the oldest or fastest language: its ecosystem may make it easier for developers to tackle
higher-value tasks.

2 Results

2.1 Constructing a space of software tasks

Software development tasks can be viewed as recurring categories of programming problems developers encounter. SO,
with its vast repository of user-generated questions, offers a unique window into these real-world challenges. To organize
this repository and facilitate retrieval, each question is labeled with one or more of 66,000 curated tags that indicate the
specific tools, frameworks, or concepts involved.

We use these tag–question relationships to group related issues into “canonical” software tasks, applying a bipartite
stochastic block model (SBM) [Peixoto, 2017, 2014, Gerlach et al., 2018] to detect communities in the graph of questions
and tags (Fig. 1a). We ignore tags that refer to programming languages and use them later on to study how tasks are
distributed across languages. To generate concise names for each task community, we prompt ChatGPT-4.0 for labels
that capture the essence of the tags comprising each group (see Appendix B). This process yields a set of 237 software
tasks, such as Develop NLP models and tools for text analysis, Establish secure server access and control, and Deploy
and secure a scalable web app.

Because certain tasks complement each other, they often co-occur within the same job roles [Anderson, 2017, Alabdulkareem
et al., 2018, Neffke, 2019, Stephany and Teutloff, 2024]. To investigate this task bundling, we identify which
tasks are frequently performed by the same SO users. This yields a network that links tasks based on their co-occurrence
in user activity. To reduce dimensionality and facilitate visualization, we then embed this network in a two-dimensional
plane.

The resulting task space contains several clusters of related tasks, each shown in a different color in Fig. 1b (see
Methods). Many of these clusters group tasks with comparable labor market returns. This is illustrated in Fig. 1d, where,
we plot task values inferred from self-reported wages in a large-scale survey run among SO users (see Methods). On the
right side of the task space, for example, three clusters revolve around website development, typically linked to lower
wages. By contrast, tasks in the top center—focusing on advanced iOS and Android development—offer significantly

higher earnings. Additional high-value clusters include those for AI and machine learning (AI/ML), Advanced Programming
Concepts, Cloud Computing, and DevOps. The table of Fig. 1e lists the five highest-paying tasks, three of which are
related to iOS app development, and five lowest-paying tasks, all associated with more basic web development.

Notably, clusters that are conceptually linked—such as AI/ML and Statistics and Data Analysis, and iOS and Android
development—tend to lie near each other in the task space. To investigate the network structure of the task space, we can

tasks

task network

tasks
a. SBM

questions tags

b.

tensorflow
pytorch
scipy
ssh
sftp
decode
ssh-key
web-scrapy
beautifulsoup
position
tableview
cell
alignment

Relatedness of Tasks

task: develop a
neural network

PMI (co-occurrence)

Clustering
(HDBSCAN)

task: set up
and automate
secure data
transfer

Dimensionality Reduction
(UMAP)

task: develop a
Flutter web
crawler

task: Implement
responsive web
layout

the top 10 most related tasks to the task “Develop AI models”

c.

Implement a custom vector library in C++

Develop video processing software

Automate Windows tasks
with Python scripts

Optimize embedded system for
predictive analytics

Develop NLP text processing system

Develop AI models

Improve Python packaging
process

Develop a clustering-
based recommendation
system

Create data visualizations
Build and visualize a
predictive model

Perform statistical analysis
and data visualization

Top-5 Tasks in Salary
Develop and optimize an iOS
application user interface.

Bottom-5 Tasks in Salary

d.

e.

Integrate various payment gateways
in an e-commerce platform
Develop a web application using
Symfony framework and Doctrine
ORM.

Develop a mobile app with modern
networking and UI frameworks.
Develop a mobile app with offline
data synchronization capabilities.
Implement scalable real-time data
processing pipelines

Implement a responsive iframe
embed for Vimeo videos.

Implement a dynamic PDF report
generator for web content
Develop responsive WordPress
themes with custom plugins and API
integrations

Implement server-side routing with
Kotlin and ASP.NET.

Figure 1: Mapping software tasks. a. Stylized depiction of the bipartite question-tag network.
SBM groups tags into communities (tasks) that connect to similar sets of questions. ChatGPT4.0
finds a common label that summarizes each community’s tag information. b. Task space.
Pointwise mutual information (PMI) expresses how surprisingly often two tasks are performed
by the same users. UMAP embeds the resulting co-occurrence network in a 2-dimensional plane
(the task space). c. Close-up on Develop AI models task, depicting the original network structure
among the 10 most closely related tasks. d. Task values. Nodes are colored according to their
task value, estimated from salary information in the SO 2023 developers survey. Darker shades
indicate more valuable tasks. e. Table of the five most and least valuable tasks. For details, see
Methods.

examine individual tasks in greater detail. For example, focusing on the ten tasks most closely related to developing AI
models, Fig. 1c reveals strong connections to other statistical tasks, as well as tasks involving image and natural language
processing, data visualization, and packaging models into standalone applications.

2.2 Validation using job ads

How well do these software tasks capture real-world development work beyond SO? To find out, we examine approximately
50,000 software job ads from HackerNews1
(see Fig. 2a and Methods). Using an LLM, we parse each job ad’s
text to extract salaries and the list of tasks required of successful candidates.

Next, we convert each job’s extracted tasks into a 237-dimensional binary vector, where each dimension corresponds
to one of the SO tasks identified previously. We accomplish this by embedding both the job’s task descriptions and
the SO task labels into a 384-dimensional space using sBERT[Reimers and Gurevych, 2019]. We then match each
extracted task to its closest SO task by comparing cosine similarities. In this way, each job ad becomes a vector of job
requirements, expressed in terms of SO tasks. Finally, we combine this vector with task-value information and measures
of task relatedness. Figure 2a (see Methods) illustrates this process.

b.

task space

sBert predict

job contents

a.

contents job contents
by tasks

c.

predict
job salary

salary
~
task value

salary

Figure 2: Job ads. a. Schematic representation of the workflow to extract salary and task requirements
from online job ads by prompting ChatGPT. Task requirements are converted to the
237-dimensional SO task vectors of Fig. 1 based on cosine similarities between text embeddings
of task requirements and SO tasks. b. Prediction of task requirements. 40% of task vector elements
are masked and grouped into 10 equally sized bins based on the fit of the masked task to
the (unmasked) task requirements of a job (see Methods). The plot displays the estimated probability
that tasks in a bin are required in the job. c. Predictions of wage offers. Jobs are grouped
into equally sized bins based on the average value of required tasks. The vertical axis shows the
estimated mean of the advertised wage offers. Vertical bars in panels b and c represent 95% confidence
intervals.

The task space strongly predicts which tasks appear together in job ads. To demonstrate this, we combine all job-task
vectors into a single dataset and randomly mask 40% of the entries. For each masked task, we then measure its relatedness
to the remaining unmasked tasks for that job. As shown in Fig. 2b, the probability that a masked task is indeed required
(i.e., has a “1” in the task vector) increases sharply with its relatedness to the other tasks, rising 70-fold from below 1%
for unrelated tasks to over 12% for strongly related ones.

The tasks we identify also predict wage offers (Fig. 2c). Salaries in job ads increase alongside the average value of
the tasks a job requires, and regression analysis confirms this: a 10% rise in the average value of these tasks is associated
with a 9% increase in the offered wage (see Appendix C.2).
1https://www.hackernews.com/

2.3 Task dynamics: growth, diversification, feedback

a.

b.

user-share change from 2009 to 2022

large
change

small
change

c.

d.

Figure 3: Task dynamics. a. Task user-share change from 2009 to 2022. Purple markers signal
increases, orange markers decreases, in user-shares between 2009 and 2022. Marker transparency
reflects the size of shifts: darker tones indicate larger changes in user shares. b. Estimated
probability of diversifying into new tasks at different values of density, users’ relatednessweighted
experience in other tasks: dθ,u =
P
κ
P
Rθ,κ
τ Rθ,τ
Xκ,u, where Xκ,u denotes user u’s experience
in task κ and Rθ,κ the relatedness between tasks θ and κ. c. Regression analysis of
answer popularity on task experience. Popularity is measured as the number of votes the answer
receives, log(#votesa + 1) or whether or not the answer is the top answer to the question,
task experience as the number of prior answers the user provided to questions on task θ in the
preceding two years, log(#answersu(a),θ,t(a)
). Control variables include log(#answersq(a)
) and
log P
α∈Aq #votesα + 1
, the total number of answers provided to question q(a)), and the sum

of all votes across these answers. To avoid problems due to log 0 values, we add 1 to counts that
can evaluate to 0. The plot shows point estimates with their 95% confidence intervals. Purple
markers refer regression analyses of whether or not an answer is the top answer, orange markers
to analyses of the number of votes. d. Regression of whether or not a user will adopt a new task θ,
on the task value, Vθ, controlling for the user’s density around the task, dθ,u. Purple markers refer
to Python-related questions only, orange markers to the full sample.

Figure 3a illustrates how SO activity shifted across software tasks between 2009 and 2022. Notable growth appears
in Web Frameworks, certain Android-related tasks, Cloud Computing, and AI/ML. Conversely, tasks associated with
Advanced Programming Concepts (e.g., Develop a data structure library for efficient data manipulation, Develop a multimedia
application in Windows, or Develop a thread-safe application to prevent race conditions), as well as Networking,
Enterprise and Web App Development, have seen their relative importance on SO decline.

We can also apply task vectors to study changes at the individual level, studying how individual SO users develop
expertise over time. To show this, we generate a task vector for each user by counting how many answers they contribute
in a two-year interval for each of the 237 defined tasks (see Methods). This approach captures the intensity of engagement
in different areas of software work. We use these user task vectors to examine how developers add new skills to their

profiles over time. In particular, we test whether task relatedness—reflected in the task space—predicts which new tasks a
user will adopt on SO. As shown in Fig. 3b, users are far more likely to pick up tasks closely related to those they already
know, with the probability of transitioning to a “new” task rising from 0.9% (when the task is unrelated) to 14.3% (when
it is highly related).

We also expect that a user’s task-specific experience should correlate with the popularity of their answers. Testing this
hypothesis is complicated, since users often decide to answer a question only after gauging existing solutions—a process
that introduces selection bias. In Appendix D.1, we address these biases using instrumental variables. Here, we mitigate
them partially by focusing on only the earliest answer posted to each question. We then ask whether users with greater
experience in tasks connected to the question receive more votes. Concretely, we regress a binary outcome—whether the
answer is the highest-voted—on the user’s prior task experience, controlling for the question’s total number of answers
and sum of votes. As a robustness check, we also predict the total votes an answer receives.

Figure 3c reveals a statistically significant, positive link between users’ task experience and the popularity of their
answers. The estimates indicate that a 10% rise in task experience boosts the likelihood of an answer becoming the
top-voted solution by 0.1 pp (±0.00004) and increases the number of votes it receives by 0.14% (±0.006%). In the SI,
section D.2 we show that when with sample-selection corrections, the estimated effects grow to 0.006 pp (±0.0035) and
0.9% (±0.41%), respectively.

Users also need motivation to adopt new tasks, whether for higher potential rewards or because the tasks align closely
with their existing skills. To examine these motivations, we regress task entry on the estimated task value (from the

aforementioned survey) and the user’s density around the task, i.e., the relatedness-weighted average experience in other
tasks the user engages with (see Methods). As shown in Fig. 3d, developers do not universally pursue high-value tasks—
likely due to the higher technological barriers or learning costs associated with them—and tend to choose tasks that are
more closely related to their current skill sets (see Appendix D.3). However, Python users follow a different pattern:
task value has a positive effect on their decision to adopt a new skill, suggesting that Python’s versatility allows them
to more readily acquire profitable tasks. This highlights Python’s distinct role in the software ecosystem: as a generalpurpose
language, it enables users to branch into new, higher-value tasks more easily, altering and expanding their career
trajectories.

2.4 Tasks and programming languages

Programmers can draw on a wide variety of programming languages, each with different levels of suitability and popularity
for specific software tasks. Our observation that Python users often diversify into higher-value tasks suggests that
language choice significantly influences developers’ career paths. Yet debates persist about which languages best serve
which tasks. Our task constructs promise a novel way to study language usage. To explore this, we use tags that refer to
specific programming languages to associate SO posts with the languages they refer to (see Methods). This allows us to
track which tasks a language supports.

Figure 4a presents a matrix illustrating which programming languages (used by at least 10 SO users) are used in each
of the 237 SO tasks. The matrix’s triangular shape signals task nestedness, with an NODF value of 81.5 [Payrato-Borr ´ as`
et al., 2020], indicating that tasks can be roughly ranked from general to specialized based on how widespread they are
across languages. Moreover, although different languages may be developed with specific use cases in mind, in practice,
this has not led to a strict specialization where tasks are divided between dedicated programming languages. Instead, the
most specialized tasks are typically handled by languages that cover almost the full spectrum of tasks, while languages
used for only a few tasks are largely confined to the most ubiquitous ones.

Figure 4b illustrates how different programming languages compete for tasks over time. Focusing on the six largest
languages on Stack Overflow, it tracks how many tasks each language dominates by user counts. The most prominent
trend is Python’s steady climb: from just nine tasks in 2009, it rises to become the top language for over 80 of the 237
tasks by 2022, surpassing well-established options like C# and JavaScript. In the SI, section F, we further demonstrate
how languages compete over tasks by focusing on the abrupt shift in iOS programming from Objective-C to Swift.

Figure 4c visualizes Python’s growth, highlighting all tasks in which it ranks among the top three languages. Initially
focused on data science, Python spread between 2014 and 2018 into tasks ranging from app development to web-related
work, DevOps, and cloud computing. Today, it is the dominant language for at least one task in every cluster. As detailed

tasks for which Python is a top 3-language

a.

c.

b.

Figure 4: Programming languages. a. Task-language matrix. Elements are colored when at least
10 SO users have at least one answer post in the task-language combination. b. Number of tasks in
which a programming language ranks as the top language in terms of SO users. The graph shows
time-series for the largest six languages in terms of cumulative SO posts between August 2008
and June 2023. c. Python’s task footprint. Nodes are colored if Python ranks among the top 3
programming languages for the associated task. Fully colored: 1st rank, 50% transparency: 2nd
rank, 75% transparency: 3rd rank.

in Appendix E, this pattern is preserved when we re-weight languages by their GitHub script counts, a proxy for real-world
usage—indicating that Python’s reach extends well beyond Stack Overflow.

3 Discussion

The growing complexity of the labor market has made measuring worker capabilities both more difficult and more important
[Anderson, 2017]. Here we demonstrated that data on individual problem solving can be used to generate a useful
fine-grained taxonomy of tasks people do in software-related work, a key industry in the digital economy. These tasks or
building blocks of software work can be given coherent economic values and capture co-occurrence relationships reflected
in real world job advertisements. We use the tasks to observe individual learning, both within tasks and entrance into new
ones. Moreover, the fine-grained detail of the task space allows us to explain an important macro-system outcome: the
rise of Python as the leading all-purpose programming language. Our explanation for Python’s success is that it enables
people to enter new tasks which have higher economic value. Ultimately, our results highlight how deepening our understanding
of the microstructure of tasks offers new ways to interpret macro-level phenomena such as technology diffusion,
wage dispersion, and the evolution of industry-wide practices.

A core insight from our results is that tasks exist in a space of related capabilities, echoing network-based accounts
of human capital [Anderson, 2017]. On the one hand, tasks are well-defined as distinctive categories of specific kinds
of work, as evidenced by their distinct labor market values and that effective learning happens by practice within tasks
[Arrow, 1962]. On the other hand, tasks also have meaningful relationships with each other, evidenced by their nonrandom
co-occurrence within job ads and observed patterns of individuals learning new tasks. The resulting networked
taxonomy of software tasks demonstrates its value by providing a micro-to-macro explanation for the rise of the Python
programming language: Python enables users to enter more valuable tasks.

Our findings connect with the literature on skill complexity, labor market transitions, and the organization of work,
complementing studies that have emphasized how granular task analysis can reveal hidden dynamics in career mobility,
wage disparities, and skill complementarities [Autor et al., 2003, Anderson, 2017, Alabdulkareem et al., 2018, del RioChanona
et al., 2021]. Previous research however, tends to use standardized task classifications such as O*NET to
define tasks and applies them to curated job descriptions, limiting the granularity and responsiveness of task taxonomies.
In contrast, by extracting tasks directly from real-world problem-solving interactions on Stack Overflow, our approach
captures the immediate and practical realities of skill application at a global scale. In rapidly changing sectors such
as software engineering, tasks derived from activities can explain surprising developments like the rise of the Python
programming language as a technology which enables diversification into more valuable tasks. This complements existing
work on task-relatedness and collective learning.

We highlight three possible applications of our method and taxonomy. First we have demonstrated that microdata
on activity can be fruitfully aggregated into tasks to describe skill acquisition, development and transitions. Tasks from
any sector in which large-scale fine-grained activity on individual behavior at work is available could be categorized in a
similar manner. Second, employers in such sectors can use our approach to identify skills related to tasks their employees
actually carry out, enabling better labor market matching outcomes or internal skill development programs. Finally,
educators can better understand the labor market landscape of the software industry using our taxonomy.

There are several limitations to our study, which may be tackled in future work. First, we have focused exclusively on
programming-related tasks. However, software developers need to be able to carry out many other tasks, such as managing
teams or reporting results. Although SO contains some postings about organizational aspects of software development,
its emphasis is on technical subjects. To explore how programming tasks are combined with other types of tasks in
software jobs, future studies could use job ads to compare the co-occurrence of our programming tasks with tasks related
to different kinds of soft skills.

Second, although the question-answer structure makes SO ideal for identifying software tasks, it may be less suited
for descriptions of macro-level trends and individual career paths. In Appendix E, we compare user numbers on SO to
GitHub. This analysis suggests that in terms of capturing software developers, both datasets are closely aligned. However,
it is impossible to judge the representativity of SO of overall software activity at the level of tasks, especially as Stack
Overflow is thought to be declining [del Rio-Chanona et al., 2024]. In Appendix E, we therefore rescale the activity in
different programming languages such that they reflect their presence on GitHub. However, in future work, we plan to

define software tasks directly in GitHub.

Third, we opted to create a task taxonomy that is time-invariant. However, an analysis of how job tasks change in
software development would provide a more vivid picture of the software industry. Such an analysis could also expand
the size of our job ad dataset. Although sufficient for the validation exercise we conducted, a larger dataset would allow
us to see how tasks in software development and their value change over time.

Notwithstanding these limitations, our study demonstrates how question-and-answer data can inform us about the
evolution of work by quantifying the abstract notion of a task. The application to the software sector sheds light on novel
aspects of high skill labor markets at high granularity, at scale, and in near real-time. Moreover, programming tasks are
rapidly diffusing beyond pure software development firms and understanding these tasks and their evolution is pivotal to
understanding the future of work in an increasingly digital economy.

4 Methods

4.1 Data

Stack Overflow Posts: Our main dataset is the corpus of questions and answers (together “posts”) on Stack Overflow
from the site’s launch in August 2008 to June 2023. The 23 million questions in this dataset are labeled by tags from
a curated system of about 66,000 tags referring to software concepts and technologies such as key-value, scipy and svm.
For each tag, SO provides a textual description, typically consisting of a few sentences. Tags are heavily moderated by
humans and automated processes, and are deduplicated through a dictionary of synonyms. We focus on tags that are used
at least 1,000 times. We split tags into a two groups: 5,083 general tags and 282 tags that refer to programming languages,
defined broadly. For the latter, we merge different versions of the same programming language, converting, for instance
python-3.x into the generic tag python. When we define tasks, we use all available posts, with answers inheriting the tags
of the questions they answer. In all other analyses, we only consider answers from users with a total of at least 10 answer
posts.

Stack Overflow Develop Survey: Stack Overflow provides access to yearly surveys of its users, the Stack Overflow
Developer Survey, with anonymous information on salaries, as well as on tools and languages used that can often be
linked to tags in SO. We use the survey data from year 2023, which contains around 12,000 participants who report their
salaries to estimate task values.

HackerNews Job Ads: We scraped job advertisements from “hnhiring.com”, an index of jobs from the website
Hacker News’ “Who is Hiring?” posts. This yielded a total of 50,998 job advertisements. We use approximately 46,000
ads to study task co-occurrence and 3,949 jobs to test the ability of tasks to predict salaries.

4.2 Building software tasks

4.2.1 Identifying programming languages

To identify tags that refer to programming languages, we rely on wiki pages, which are available for most common tags.
We first filter the pages to find tags that include “language” or “framework” among their keywords. We then manually
review all the tags to select those that refer to programming languages, yielding a total of 282 programming languages.

Some programming tags refer to specific versions of a language, such as “python-3.x” or “python-3.7”. When calculating
the nestedness of the task-language matrix, we merge all tags referring to different versions of the same programming
language. Yet, there is some ambiguity to what counts as a programming language, such as frameworks and
developer environments. We remove such tags when calculating nestedness, basing this estimate on a task-language
matrix with 114 programming languages.

4.2.2 Identifying software tasks

To identify canonical software tasks, we express the relation between questions and their tags as a bipartite network with
18,154,593 question nodes that connect to 5,083 tags through 33,378,590 edges. We then apply a bipartite Stochastic

Block Model (SBM) to identify communities of tags.

SBMs essentially estimate a coarsened version of a network. To do so, they identify communities of nodes and
parameters that represent parsimonious descriptions of edge distributions within and between communities. To sharpen
the boundaries of inferred communities, we remove 20% of tags that have the weakest own-community attachment (see
Appendix section A). Dropping communities with fewer than 3 tags, we retain 237 tasks, connected to 4,054 tags, out of
originally 247 detected communities.

4.3 User task vectors

We use the tasks extracted from the question-tag network to describe the activity of individual SO users as a 237-
dimensional vector. Entries of this vector count how many answers the user has provided to questions that are labeled
with tags that are associated with each corresponding task. Specifically, we express the user’s task experience in time
period t as:

Xt
u,1
Xt
u,θ
Xt
u,Nθ

T⃗t
u =

, (1)

where Nθ = 237 the total number of tasks and Xt
u,θ is the number of answers posted in period t by user u to questions
labeled with a tag belonging to the community of tags associated with task θ.

4.4 Constructing a Task Space

To calculate the relatedness between tasks, we analyze which tasks are often associated with the same users. To do so, we
collect the task vectors of all users in an (Nθ × Nu) matrix T, with Nu the number of users in the dataset with at least 10
answers and Nθ = 237 the total number of tasks. Next, we ask how often two tasks co-occur within the same users by
multiplying (T > 0) with its transpose: (T > 0)(T > 0)′
. Finally, we calculate the Pointwise Mutual Information (PMI)

of probability pθ,κ that task θ and κ co-occur in the same user to capture the amount of (information-theoretic) surprise
involved in observing the joint probability pθ,κ against a benchmark where draws of tasks θ and κ are independent:

PMIθ,κ = log pθ,κ
pθpκ

, (2)

P
µ
pµ,κ.
To estimate PMI values and their credible intervals, we apply a Bayesian statistical framework developed by [van
Dam et al., 2023].

where pθ and pκ are marginal probabilities, i.e., pθ =

P
γ

pθ,γ and pκ =

The task space is based on a weighted network where nodes represent tasks and edges the relatedness between them.
Because our focus is on relatedness as expressed in a surprisingly large observed probability that two tasks co-occur, we
ignore tasks that co-occur less frequently than our random null model predicts by setting all negative PMI values to 0.
To identify clusters in the task space, we embed the relatedness network in a 5-dimensional space using UMAP [McInnes
et al., 2018]. Next, we cluster sets of contiguous tasks using HDBSCAN [McInnes et al., 2017]. These clusters are
represented in colors of Fig. 1b. The nodes’ coordinates in this figure are determined by a UMAP embedding of the
relatedness network in a 2-dimensional space.

4.5 Task Values

We estimate the value of a task based on salary information from the Stack Overflow developers survey. We focus on the
12,000 US participants that report a salary in 2023. Respondents list the technologies they use, which often correspond to
tags in the SO platform. For each SO user, we use the top 300 most similar survey respondents in terms of overlap in tags
and technologies to estimate user salary. We use the weighted average salary reported by the most similar respondents,
weighting by tag similarity to the SO user. To assign values to tasks, we then calculate the weighted average salary of the

users that carry out that task, using the prevalence of the task in users’ task vectors for the years 2018-2023 (the period in
which we collect job ads) as weights:

Vθ =
X
u
X
2018,2023
u,θ
P
u′ X
2018,2023
u′
,θ

Vu (3)

Vu =
X
ρ∈Ru
P
Mu,ρ
α Mu,α

Vρ, (4)

where Mu,ρ is the number of overlapping tags between SO user u and one of the 300 closest survey respondents, ρ ∈ Ru,
and Vρ is the salary of survey respondent ρ, such that Vu, the match-weighted average salary of survey respondents
matched to user u, can be interpreted as a proxy for the user’s salary.

4.6 Job Advertisements

The data on job ads come from the website HackerNews, and were scraped from the aggregator site hnhiring.com.
They represent all 50,998 job ads posted to the website between January 2018 and May 2024. These ads are unstructured
job descriptions sometimes including salary and expected work activities (tasks). We prompted an LLM (ChatGPT-3.5)
to extract salary information and task requirements, which yields about 46,000 jobs listing at least 3 tasks, and 3,949
jobs that contain at least 1 task and salary information. When ads describe more than one position, the LLM provides
information on each job separately.

We first relate the task requirements of job ads to the 237 SO tasks. We embed both job ad tasks and SO tags in a
384-dimensional vector space using sBERT [Reimers and Gurevych, 2019]. To describe an SO task in this vector space,
we calculate the embedding of its label. To increase accuracy, we use somewhat longer labels of up to 30 words generated
by ChatGPT-4.0. Finally, we match each task requirement of a job ad to the closest SO tasks based on cosine similarity
between the embeddings of the job-ad task and of the SO task. When we cannot find any SO task with a cosine similarity
of at least 0.3, we drop the task requirements. This yields a 237-dimensional vector of zeros and ones that describe each
job’s requirements in terms of our SO tasks. In Appendix C.3, we demonstrate robustness of our findings to alternative
methods and thresholds.

We use these data in two ways to test the validity of our SO tasks. First, we ask whether we can predict the task
composition of a job. To do so, we take the SO-task vectors associated with each job ad and stack these vectors into a
dataset that contains for each combination of an SO task and an advertised job whether or not the task is required by the
job. Next, we mask 40% of observations in this dataset and calculate the density of required tasks in the job around the
masked tasks:

Dθ,j = R¯

θ,jTj , (5)

where¯denotes row-normalization and Tj and Rθ,j are the unmasked portions of job j’s task vector and the corresponding
rows of relatedness matrix R, namely Rθ,i = P
Rθ,i
τ Rθ,τ
. Dθ,j denotes the average relatedness of (masked) task θ to all
unmasked tasks in job j.

We plot how the estimated probability that a job requires a particular (masked) task changes with that task’s density
in the job’s unmasked task requirements. To do so, we bin all masked observations in 10 equally sized bins and calculate
relative frequencies with their 95% confidence intervals. These estimated probabilities are plotted on the vertical axis of
Fig. 2b, against the bin’s average task density on the horizontal axis.

Our second validation focuses on the set of advertised jobs that also post salary information. It estimates the association
between the average value of a job’s SO tasks and the posted wage in the job ad. We report on this in SI,
section C.2.

4.7 Analysis of SO users

To study user behavior, we randomly divide the population of users into two equally sized samples. We use the first
sample, S1, to construct a task relatedness matrix from co-occurrence patterns of tasks in users. The second sample, S2,
is used to estimate how relatedness affects user activity on SO. To do so, we collect information from all answer posts

by these users within rolling two-year intervals. That is, we construct experience vectors T⃗t
u
, where t denotes an interval
that stretches across the two calendar years preceding year t. For instance, T⃗ 2018
u
refers to the answers user u provides
between January 1, 2016 and December 31, 2017.

4.7.1 Task diversification

Analogously to eq. (5), we use sample S2 to calculate for a given user, u, and year t, the experience density around each
task:

D
t
u = R¯
S1T
t
u
, (6)
where R¯
S1
is the row-normalized relatedness matrix, constructed using users in sample S1.
Next, we ask which new tasks users are most likely to enter. To do so, we take all tasks in which user u had no activity
in the two calendar years preceding t. These tasks represent the set of tasks that user u can enter. We tag all such tasks
with a 1 whenever the user posts at least one answer related the the task in year t, and with 0 otherwise. Next, we divide
all user-task combinations at risk of entry into 10 equally sized bins and estimate the probability that users do enter these
tasks in year t. Figure 3b shows how these estimated probabilities rise with the user’s experience density around a task.
95% confidence intervals are approximated with a normal distribution, using the following estimate of the standard error
of the mean:
σˆb =
√
nb
p
πˆb(1 − πˆb), (7)

where nb the number of observations in bin b and πˆ =
db
nb
, where db the number of entered tasks in bin b, the relative
frequency with which tasks in bin b are entered.

4.7.2 Voting

To study of a user’s proficiency and learning in a task, we analyze the votes the user’s answers receive. Votes are social
feedback from other users indicating appreciation for a post. However, the sample of answers that users post is highly
selected. First, before deciding to post an answer, users will look at existing answers to a question to see if they can
improve or add to them. To avoid sample selection bias from this, we limit ourselves to the first recorded answers for each
question. Second, users will post answers to question for which they perceive themselves to be sufficiently knowledgeable.
We address this type of sample selection bias in Appendix D.2, where we use variation in the user base’s activity patterns
across the 24-hour daily cycle.

To determine the importance of users’ task experience, we estimate its effect on the upvotes their answers receives.
To do so, we estimate the following regression model, with outcomes reported in Fig. 3c:

ya,θ = βx log(Xθ,u(a) + 1) + βa log(Aq(a)) + βv log(1 + X
i∈Qq(a)
vi) + ηa, (8)

where Xθ,u(a)
is user u(a)’s experience in terms of the number of answers provided to questions involving task θ in the
two calendar years preceding the calendar year in which answer a was provided, Aq(a)
the number of answers provided
to question q(a), Qa the set of answers provided to question q(a), vi
the number of upvotes that answer i received and ηa

a disturbance term. Furthermore, the dependent variable ya,θ is either a binary variable that indicates whether answer a
is a question’s top answer or log(va + 1), the logarithm of the number of upvotes answer a receives, augmented by 1 to
avoid log(0) issues. Note that if an answer is associated with multiple tasks, we replicate the observation accordingly.

4.7.3 Task adoption analysis

To study which new tasks users adopt, we estimate the effect of task value and density on new task entries, estimating the
following regression model:

yu,θ = βV log(Vθ) + βDDu,θ + σu,θ, (9)

where yu,θ is a binary variable that encodes whether or not user u adopted task θ, log(Vθ) is the logarithm of the task’s
value as defined in eq.( 3), and Du,θ the user u’s density around task θ as defined in eq. (6) before. We estimate this

model once with data from all programming languages and once with data on answers related to Python only. Findings
are summarized in Fig. 3d, with detailed results described in Appendix D.3.

Acknowledgements

XF, JW, SD and FN acknowledge financial support from the Austrian Research Agency (FFG), project #873927 (ESSENCSE).
JW acknowledges support from the Hungarian National Scientific Fund (OTKA FK 145960). SD acknowledges financial
support from the Dutch Research Council (NWO) under the REWIRE project, grant number KICH1.MV02.22.010.

# tasks -0.0059 -0.0067∗
-0.0066∗
(0.0034) (0.0032) (0.0033)
Fixed-effects

year Yes Yes Yes Yes Yes Yes
Fit statistics

Observations 4,116 4,116 4,116 4,116 4,116 4,116
R
2 0.12595 0.11509 0.12610 0.11501 0.12745 0.12756
Within R2 0.01367 0.00142 0.01384 0.00133 0.01536 0.01548

Robust standard errors in parentheses. p-value: ***: 0.01, **: 0.05, *: 0.1. The dependent variable is the value or
midpoint of the salary range posted in a job ad, task value is the average of the logarithm of the task values across all SO
tasks the job requires, task coherence is the average of the task density round all SO tasks the job requires, # tasks is the
logarithm of the number of SO tasks the job requires.

C.3 Alternative job task matches and thresholds

We test three alternative methods to match task requirements in job ads to SO tasks. To do so, let v
j
t denote the embedding
vector of task requirement t of job j. Our first method, used in the main text, calculates the cosine similarity between
v
j
t
and the embedding vector of each of the SO task’s (long) labels, and then selects the SO task that yields the highest
cosine similarity. Our second method uses the similarity of v
j
t
to the embedding of the most prominent tag (in terms of
its usage on SO) in each SO task. Our third method calculates the similarity of v
j
t
to the average embeddings of the tags
defining the SO task. Finally, our fourth method uses the similarity of v
j
t
to the embedding of the closest tag in each SO
task. Next, we repeat the analysis depicted in Fig. 2 with each of these methods. Figure C.1 presents the results.

match to SO task description
from GPT (Results in Fig 2)

match to most frequent tag in
each SO tasks

match to average tag
embeddings of SO tasks

match to closest tag from all
SO tasks

a.

c.

e.

g.

b.

d.

f.

h.

Figure C.1: Alternative methods to match task requirements in job ads to SO tasks. a,c,e,g. Prediction
of task requirements. 20% of task vector elements are masked and grouped into 10 equally
sized bins based on the average relatedness of the masked task to the (unmasked) SO task requirements
of a job. Plot displays the estimated probability, with its 95% confidence interval, that tasks
in a bin are required in the job. b,d,f,h. Predictions of wage offers. Jobs are grouped into equally
sized bins based on the average value of the tasks they require. Vertical axis shows the estimated
mean salary posted in the job ads, with their 95% confidence intervals. a,b. Task requirements are
matched to SO tasks using the embedding vector of the SO task’s label, namely the results shown
in Fig 2. c,d. Task requirements are matched to SO tasks using the embedding vector of the SO
task’s main (most frequent) tag. e,f. Task requirements are matched to SO tasks using the average
embedding vector across all of the SO task’s tags. g,h. Task requirements are matched to SO tasks
using the closest embedding vector across all tags of SO tasks.

In the main text, we only keep task requirements that can be matched with SO tasks at a cosine similarity of 0.3 or
above. To explore the significance of this threshold, we repeat our analyses with two another thresholds: 0.2 and 0.4. The
results are shown in Fig. C.2. Varying the threshold around the 0.3 value of the main text does not meaningfully alter the
outcomes of this analysis: density around masked tasks is strongly predictive of jobs demanding these tasks and salaries
posted in job ads rise with the average values of the SO tasks we identify for them.

similarity threshold = 0.3
(results in Fig 2.)

similarity threshold = 0.2 similarity threshold = 0.4

a.

c.

e.

47,928 jobs

54,985 jobs 28,132 jobs

b.

d.

f.

4,116 jobs

4,326 jobs 3,257 jobs

Figure C.2: Results of task and salary prediction at varying matching thresholds. a,c,e. Probability
that a masked SO task is listed among a job’s task requirements. Masked tasks represent 40% of
task vector elements and grouped into 10 equally sized bins based on the average relatedness of
(density around) the masked task to the (unmasked) task requirements of a job. Plot displays
estimated probabilities in each bin. b,d,f Predictions of salaries. Jobs are grouped into equally
sized bins based on the average value of their required matched SO tasks. Vertical axis shows the
estimated means in each bin of the advertised wage offers. a,b. Task requirements are matched
to SO tasks with a minimum cosine similarity of 0.3, namely the results shown in Fig. 2. c,d.
Task requirements are matched to SO tasks with a minimum cosine similarity of 0.2. e,f. Task
requirements are matched to SO tasks with a minimum cosine similarity of 0.4. Vertical bars
represent 95% confidence intervals.

D Analysis on SO users

D.1 Alternative specifications for voting regression

In Fig. 3c of the main text, we study how the popularity of an answer relates to the task experience of the user that provided
it. The figure shows that answers by users with more task experiences tend to receive more upvotes and are more likely to
be the top answer to a question. Table D.1 provides the full set of regression results related to this analysis.

Because for questions that receive only a single answer, this answer is automatically the top answer, we repeat the
analysis in a sample that excludes any question that receives only one answer. Table D.2 shows that this leads to larger
observed effects of task experience.

D.2 Causal effects: Instrumental variable estimation

In the main text, we raise the issue of sample selection bias in the regression analysis of the number of upvotes an answer
receives on SO. There are two concerns. First, users can observe all existing answers to a question and, arguably, users will
take these answers into consideration before deciding whether or not to provide an answer themselves. As a consequence,
the answers we observe on SO are no random sample of user-answer combinations. For instance, we expect that users
who believe they have little to add to the existing answers to a given question will tend to refrain from posting their own
answers. This bias is addressed by only focusing on the first answer (in a temporal sense) that each question received.

Table D.1: Voting regressions.

Dependent Variables: top answer (binary) # votes (log)
Model: (1) (2) (3) (4)
Variables

task experience 0.0097∗∗∗ 0.0104∗∗∗ 0.0130∗∗∗ 0.0137∗∗∗
(0.0008) (0.0002) (0.0016) (0.0003)
# answers -0.4886∗∗∗ -0.4915∗∗∗ -0.7939∗∗∗ -0.7982∗∗∗
(0.0036) (0.0019) (0.0199) (0.0037)
# votes all answers -0.0400∗∗∗ -0.0402∗∗∗ 0.8604∗∗∗ 0.8596∗∗∗
(0.0023) (0.0006) (0.0037) (0.0011)
Fixed effects

year Yes Yes
year-task Yes Yes
Fit statistics

Observations 7,984,391 7,984,391 7,984,391 7,984,391
R
2 0.28841 0.28936 0.81479 0.81518
Within R2 0.27190 0.26689 0.80879 0.80359

p-value: ***: 0.01, **: 0.05, *: 0.1
Regression model of eq. (8). The dependent variable is either a binary variable that encodes whether or not an answer
has received the most upvotes among all answers provided to a question, or the logarithm of the number of upvotes
the answer received. task experience: logarithm of task experience, the total number of answers the users provided to
questions related to the focal task in the past two calendar years. # answers: logarithm of the total number of answers
provided to the focal answer’s question. # votes all answers: logarithm of the total number of votes received by these
answers. Regression models contain either year or task-year fixed effects.

Table D.2: Voting regressions when questions receive at least two answers.

Dependent Variables: top answer (binary) # votes (log)
Model: (1) (2) (3) (4)
Variables

task experience 0.0260∗∗∗ 0.0279∗∗∗ 0.0313∗∗∗ 0.0336∗∗∗
(0.0009) (0.0004) (0.0026) (0.0007)
# answers -0.2437∗∗∗ -0.2491∗∗∗ -0.6309∗∗∗ -0.6371∗∗∗
(0.0043) (0.0021) (0.0216) (0.0036)
# votes all answers -0.0814∗∗∗ -0.0816∗∗∗ 0.7513∗∗∗ 0.7503∗∗∗
(0.0065) (0.0011) (0.0046) (0.0014)
Fixed-effects

year Yes Yes
task-year Yes Yes
Fit statistics

Observations 3,170,868 3,170,868 3,170,868 3,170,868
R
2 0.09076 0.09334 0.67850 0.67968
Within R2 0.08081 0.08076 0.66944 0.66110

p-value: ***: 0.01, **: 0.05, *: 0.1
Idem Table D.1, but excluding answers to questions that receive only a single answer.

Second, even the first answer to a question will not be randomly sampled from a population of users and the answers
they would have provided had they chosen to do so. Instead, answers will be provided by users who believe they have
useful insights to the problem at hand. To address the sample selection bias this causes, we will exploit the fact that, due
to timezone differences, most users are active on the SO platform at somewhat predictable times. Therefore, we expect
that who will provide the first answer to a question to some extent depends on the time of day the question was posted.
This introduces some exogenous variation in the likelihood that a given user provides an answer to a given question.
Moreover, as far as task experience is not fully equally distributed across timezones, this offers exogenous variation in the
task experience associated with the first answer to a question.

We proceed as follows. First, we label each minute of a day, henceforth day-minute, from 0 to 1399 in a manner
that is independent of timezones. Next, for each user, we calculate the average minute of the day they post answers on
SO. This offers a coarse indication of when a user is active on the platform. Finally, we calculate for each task and each
day-minute the amount of task experience that is expected to be available on SO. To do so, we sum the task experience
of all users, weighted by the gap between the day-minute of a question and the average day-minute of each user. We call
this variable, Mθ,m, the minute-task count of task θ at day-minute m. Next, we use this variable as an instrument for the
actual task experience of whichever user provides the first answer to the question at hand.

Note that there are some potential concerns about this instrument. First, if there are geographic components to task
experience of users and if these geographic components directly influence the quality of an answer, the instrument may
be invalid. For instance, the timezone that includes Silicon Valley may have a disproportionate number of highly skilled
programmers, such that any questions posed when most people in this timezone are active may attract high quality first
answers. To correct for this, we always include day-minute fixed effects and in some specifications also add task-yearcombination
fixed effects.

Second, the instrument assumes that questions are answered within day from the time they are posted on SO. In fact,
we would expect that our instrument does not work for questions whose first answer does not arrive within 24 hours. We
exploit this in placebo tests that focus on questions whose first answer is provided at least 24 hours after the posting of the
question itself.

Table D.3 shows results for an adapted version of the regression model of eq. (8) in the main text, but now using
Two-Stage Least Squares (2SLS) estimation. In particular, we estimate the following equation:

ya,θ = βx log(Xθ,u(a) + 1) + βa log(Aq(a)) + βv log(1 + X

vi) + µq(a) + ηa, (15)

i∈Qq(a)

where u(a) is the user who posts answer a, Xθ,u(a) user u(a)’s experience in terms of the number of answers provided to
questions involving task θ in the two calendar years preceding the calendar year in which answer a was provided, Aq(a)
the number of answers that will eventually be provided to question q(a), Qa the set of these answers, vi
the number of
upvotes that answer i received and ηa a disturbance term. Compared to eq. (8) in the main text, we add day-minute fixed
effects, µ(qa
), that control for any timezone specific confounders.

As before, the dependent variable ya,θ is either a binary variable that indicates whether answer a is the top answer to
its question or log(va + 1), the logarithm of the number of upvotes answer a receives, augmented by 1 to avoid log(0)
issues. If an answer is associated with multiple tasks, we replicate the observation accordingly.

The results is presented in Table D.3. The effect of task experience on answer popularity is significant and positive
across all model specifications. Moreover, the estimated causal effects arrived at by instrumental variables estimation are
substantially larger than the OLS estimates reported in the main text. This is in line with a downward sample-selection
bias in the OLS results.

Next, we test this strategy using our placebo tests. To do so, we split the sample of questions into questions that
receive a first answer within the first 24 hours after they were posted and those that receive their first answer later than
that. Results are shown in Table D.4. For answers provided within 24 hours, task experience has a strong and statistically
significant positive effect on answer popularity, regardless of whether we look at the probability of being the top answer or
the number of upvotes an answer receives. In contrast, for the placebo test, comprising of answers provided more than 24
hours after the question was posted, the effect of task experience becomes insignificant in three out of four models. In the
model without task fixed effects, the effect on the number of votes an answer receives turns significantly negative. This
suggests that the task fixed effects control for some relevant confounders. Therefore, our preferred estimates are derived

Table D.3: Instrumental variable regression.

Dependent Variables: top answer (binary) # votes (log)
Model: (1) (2) (3) (4)
Variables

task experience 0.0162∗∗∗ 0.0601∗∗∗ 0.0306∗∗∗ 0.0919∗∗∗
(0.0005) (0.0179) (0.0006) (0.0209)
# answers -0.4847∗∗∗ -0.4598∗∗∗ -0.7835∗∗∗ -0.7484∗∗∗
(0.0006) (0.0114) (0.0008) (0.0133)
# votes all answers -0.0418∗∗∗ -0.0536∗∗∗ 0.8555∗∗∗ 0.8385∗∗∗
(0.0002) (0.0048) (0.0003) (0.0056)
Fixed-effects

year Yes Yes
QA-abs-minute Yes Yes Yes Yes
task-year Yes Yes
Fit statistics

Observations 7,984,391 7,984,391 7,984,391 7,984,391
R
2 0.28734 0.22128 0.81305 0.78261
Within R2 0.27051 0.19626 0.80680 0.76881

Clustered (group task qminute) standard-errors in parentheses
Signif. Codes: ***: 0.01, **: 0.05, *: 0.1
Results of eq. (15) estimated with 2SLS. The dependent variable is either a binary variable that encodes whether or not
an answer has received the most upvotes among all answers provided to a question, or the logarithm of the number
of upvotes the answer received. task experience: logarithm of task experience, the total number of answers the user
provided to questions related to the focal task in the past two calendar years. # answers: logarithm of the total number
of answers provided to the focal answer’s question. # votes all answers: logarithm of the total number of votes received
by these answers. Regression models contain day-minute fixed effects (QA-abs-minute) for the timing of the question
and year or task-year fixed effects. To overcome sample-selection biases, we instrument task experience with Mθ,m, the
estimated amount of available task experience at the moment the question was posted, calculated as the weighted sum of
task experience across all users, where weights reflect the temporal distance between the day-minute of a user and of the
question’s posting.

from models that include these fixed effects. These models suggest a large and positive effect of task experience on the
popularity of answers, corroborating our analysis in the main text.

Table D.4: Instrumental variable regression: placebo tests.

Dependent Variables: top answer (binary, ≤ 24 hours) # votes (log, ≤ 24 hours) top answer (binary, ≥ 24 hours) # votes (log, ≥ 24 hours)
Model: (1) (2) (3) (4) (5) (6) (7) (8)
Variables
task experience 0.0183∗∗∗ 0.0620∗∗∗ 0.0314∗∗∗ 0.0947∗∗∗ 0.0009 0.0561 -0.0172∗∗∗ -0.0030
(0.0005) (0.0174) (0.0006) (0.0203) (0.0038) (0.2365) (0.0048) (0.2827)
# answers -0.4800∗∗∗ -0.4528∗∗∗ -0.7750∗∗∗ -0.7347∗∗∗ -0.5116∗∗∗ -0.4920∗∗∗ -0.8835∗∗∗ -0.8773∗∗∗
(0.0007) (0.0123) (0.0008) (0.0143) (0.0023) (0.0848) (0.0032) (0.1014)
# votes all answers -0.0448∗∗∗ -0.0573∗∗∗ 0.8471∗∗∗ 0.8284∗∗∗ -0.0231∗∗∗ -0.0275 0.9150∗∗∗ 0.9140∗∗∗
(0.0002) (0.0050) (0.0004) (0.0058) (0.0004) (0.0190) (0.0007) (0.0227)
Fixed-effects
year Yes Yes Yes Yes
QA-abs-minute Yes Yes Yes Yes Yes Yes Yes Yes
task-year Yes Yes Yes Yes
Fit statistics
Observations 6,915,424 6,915,424 6,915,424 6,915,424 1,068,555 1,068,555 1,068,555 1,068,555
R
2 0.28071 0.21444 0.80404 0.77090 0.32491 0.24001 0.86829 0.87025
Within R2 0.26317 0.18891 0.79722 0.75538 0.31531 0.22360 0.86502 0.86413
Clustered (group task qminute) standard-errors in parentheses
p-value: ***: 0.01, **: 0.05, *: 0.1

Idem Table D.3, but splitting the sample into questions that were answered within 24 hours and those that weren’t. The
results for the latter sample, depicted in the in columns (5)-(8), represent placebo tests for the instrumental variables
estimation.

D.3 Regression of entry on task value

To study how task values effect users’ adoption on new tasks, we run the regression described in eq. (9) of the main text.
We compare the association of two variables, task value and task density, with the likelihood that users adopt a certain
task. We repeat this analysis once using all answers to construct experience and task entry variables, and once using only
answers to Python related questions. The results are shown in Table D.5.

E Rescaling by Github

Figure 4 shows Python’s progressive rise as the dominant language for an increasing number of programming tasks.
However, even though SO may provide a useful dataset to define such programming tasks, it is not guaranteed to be
representative of programmers across the world. To assess this problem, we compare counts of programmers on SO to
comparable ones on GitHub. GitHub is the world’s largest software development collaboration platform and therefore
offers a good representation of the global software development sector. In particular, we collect information on the
(self-reported) countries of residence on GitHub and (observed) language use between 2020 and 2022 [GitHub, 2025].
Figure E.1a compares SO to GitHub user counts at the level of countries, languages and country-language combinations.
This shows that user numbers are highly correlated across the two platforms, with correlations ranging from 0.75 to 0.93.
Nevertheless, some languages are better represented on SO than others. This may affect our analysis of how dominant
a language is for a given task. In Fig. E.1b we attempt to correct for this, by reweighting the user counts by language using
their observed shares on GitHub. This reweighting ensures that the distribution of users across language on SO mimics
the one on GitHub. Because we only have GitHub information for the years 2020, 2021 and 2022, the analysis is limited
to those years. Also with reweighted user counts, Python leads in most tasks, albeit with round 50, in somewhat fewer
tasks than what we report in the main text. The ordering of the remaining languages is mostly unchanged as well, except
for C#, which was somewhat more prominent before rescaling user counts. Moreover, also the most prominent temporal
patterns over the 3-year time period are mostly left unchanged. Figure E.1b retains the rise of Python and the drops of
Java and PHP, as well as the relative stability in these years of JavaScript, validating the results shown in the main text.

Table D.5: Task entry regressions

Dependent Variable: entry (binary, all programming languages) entry (binary, Python)
Model: (1) (2) (3) (4) (5) (6) (7) (8)
Variables

task value -0.0078∗∗∗ -0.0079∗∗∗ -0.0068∗∗∗ -0.0069∗∗∗ 0.0342∗∗∗ 0.0348∗∗∗ 0.0140∗∗∗ 0.0146∗∗∗
(0.0008) (0.0008) (0.0006) (0.0006) (0.0011) (0.0011) (0.0009) (0.0011)
density 0.0194∗∗∗ 0.0173∗∗∗ 0.0181∗∗∗ 0.0176∗∗∗
(0.0002) (0.0002) (0.0004) (0.0006)
Fixed-effects

user Yes Yes Yes Yes
Fit statistics

Observations 24,367,254 24,367,254 24,367,254 24,367,254 2,229,882 2,229,882 2,229,882 2,229,882
R
2 1.8 × 10−5 0.01688 0.01859 0.02743 0.00047 0.01627 0.02210 0.03082
Within R2 1.86 × 10−5 0.01076 0.00049 0.01528

Detailed outcomes of the regression model described in eq. (9) of the main text. Observations are user-task combinations
for which the user did not answer any questions related to the task in the previous two years. The dependent variable is
a binary value of whether or not the user enters the task (i.e., answers questions related to this task) in the current period.
task value: logarithm of the task’s imputed value, task density: the user’s prior experience in other tasks, weighted by
the relatedness of these tasks to the current task. For ease of interpretation, we subtract the variable’s mean and then
divide by its standard deviation. Models in columns (2), (4), (6) and (8) control for user fixed effect. Columns (1)-(4)
report analyses performed using all answer posts, columns (5)-(8) use only Python related answer posts. Clustered (user)
standard-errors in parentheses. p-values: ***: 0.01, **: 0.05, *: 0.1.

a. User counts: Stack Overflow versus GitHub b.

Figure E.1: a. The GitHub user counts against the SO user counts in the perspectives of country,
programming languages and country-language in the year 2022. The values are in log scale and
the R2 values of the regression fit are provided inside each panel. b. Number of tasks in which a
programming language is the top language in terms of SO users reweighted by user counts from
GitHub, from 2020 to 2022. The graph shows the largest 6 languages measured by cumulative SO
posts between August 2008 and June 2023.

F Swift vs Objective-C

comparison between swift and objective c

#tasks

swift
objective c

2010 2012 2014 2016 2018 2020 2022
year

Figure F.1: Number of tasks in which Objective-C has more users on SO than Swift and vice versa.
The dashed vertical line marks the year 2014, the year that Swift was released.

Software written for Apple devices was mostly written in Objective-C from the 1980s until the mid 2010s. Apple
designed Swift to replace Objective-C and launched the language in 2014. Within the next few years, most users switched
to this new language to be able to continue developing software for Apple products [JetBrains, 2023]. Unlike typical
programming language dynamics, which evolve organically from developer communities, Swift’s introduction was a
deliberate, top-down intervention by Apple.

Figure F.1 describes this shift in terms of the tasks where Swift was more popular than Objective-C and vice versa.
Before 2015, most tasks were handled preferentially in Objective-C. However, since the release of Swift in 2014 this
rapidly changes. Swift surpasses Objective-C in terms of the number of different tasks it handles around 2015 and all but
eclipses Objective-C by 2016.
