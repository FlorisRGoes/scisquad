
# SciSquad
This is a Python package developed by SciSports for the purpose of Squad Management. Please refer 
to the *Squad Management* section for more detailed information like the problem statement, use-cases and applications.

## Basic Usage

To use the functionality of this package, one needs to have a valid API client for the SciSports Recruitment Center
platform. Please contact support@scisports.com for more information if you do not already have an account, or you
don't have a valid API client. Note that accounts & API access are part of commercial subscriptions to SciSports
products, and costs might apply.

For the package to work, please clone the repository and make sure your local environment has a .env file with the
following variables:

* API_USER
* API_PW
* API_CLIENT_ID
* API_CLIENT_SECRET
* SCISPORTS_USER_ID
* SCISPORTS_ACCOUNT

Additionally, if you want to use custom explanations using the functionality in the `explanations` module, you need
to have an Azure Open-AI subscription, and need to include the following variables in your .env file:

* LLM_KEY
* LLM_ENDPOINT
* LLM_MODEL

## Squad Management
Squad Management is about being able to evaluate the current roster of a professional football team, 
and to plan ahead for the coming 6-12 months ahead. Essentially, this means Squad Management is about making decisions 
with regards to (1) contract extensions, (2) buying and selling players and (3) attributing a certain 
amount of minutes to a given player. 

This demonstrator package provides the core functionality for managing a squad, and suggests the following flow to be
adopted by the user:

1. Retrieve all team information, like fixtures in the various competitions, the current roster, development of the team etc. 
2. Benchmark the team against other teams in the same league, using the main (domestic) league a team participates in.
3. Analyze the team's strong and weak spots using the league benchmarks, and find recommended scouting filters from past behavior.
4. Let the system analyze the state of current squad, and generate alerts for the user to act upon.
5. Create a scouting plan based on the outcomes above, and let the system execute a search based on the suggested parameters.
6. Simulate addition of various of the top scouting targets to the roster, to understand what the effect of certain decisions by the user would be.

## Demos

Note that demonstrations and tutorials can be found in the `demos` folder in this repository. They are open access and
can be used for demonstration purposes by anyone, no login or subscription is required.

## Acknowledgement
The demonstrators featured in this project are connected to the contributions of SciSports to 
the [TUPLES Trustworthy AI Project](https://www.tuples.ai). This project has received funding from the 
European Union’s HORIZON-CL4-2021-HUMAN-01 research and innovation programme under grant agreement No. 101070149

## 📜 Notice

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.

- ✅ You’re welcome to use, modify, and share this project for **personal, academic, or research purposes**.  
- ❌ **Commercial use is not allowed** — that means you can’t use this project (or parts of it) in products, services, or activities that are intended for profit.  
- ℹ️ Full license details: [CC BY-NC 4.0 Legal Code](https://creativecommons.org/licenses/by-nc/4.0/legalcode)  

If you’d like to use this project in a commercial setting, please reach out to the author to discuss licensing options.  
