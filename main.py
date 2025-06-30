from agent.job_input import preprocess_job_description
from agent.search_linkedin import search_linkedin
from agent.score_candidates import score_candidates
from agent.generate_outreach import generate_outreach

def process_job(job_url):
    job = preprocess_job_description(job_url)
    candidates = search_linkedin(job['title'])
    scored = score_candidates(candidates, job['summary'])
    messages = generate_outreach(scored[:5], job['summary'])
    return {
        'job': job,
        'top_candidates': messages
    }

job_url = "https://app.synapserecruiternetwork.com/job-page/1750452159644x262203891027542000"
result = process_job(job_url)
print(result)