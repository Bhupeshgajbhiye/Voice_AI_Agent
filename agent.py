import os
import asyncio
import csv
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RunContext,
    cli,
    inference,
    function_tool,
)
from livekit.plugins import silero

# Force Python to find .env.local in the exact same folder as agent.py
env_path = os.path.join(os.path.dirname(__file__), ".env.local")
load_dotenv(env_path)


# 1. Custom tool to save candidate answers directly to a CSV file
@function_tool
async def save_candidate_answer(
    context: RunContext, 
    question: str, 
    answer_summary: str, 
    score: int
):
    """
    Call this function after the candidate answers a question to log their response and your evaluation.
    """
    # Print to terminal so you can monitor it live
    print(f"\n--- 📝 INTERVIEW LOG ---")
    print(f"Question: {question}")
    print(f"Summary: {answer_summary}")
    print(f"Score: {score}/10")
    print(f"------------------------\n")
    
    # Save permanently to a CSV file in your project folder
    file_name = "candidate_answers.csv"
    file_exists = os.path.isfile(file_name)
    
    with open(file_name, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write the header row if the file is brand new
        if not file_exists:
            writer.writerow(["Question", "Candidate Answer Summary", "Score"])
            
        # Write the actual data row
        writer.writerow([question, answer_summary, score])
    
    return "Successfully saved to database. Proceed to the next question."


# 2. Initialize the LiveKit server
server = AgentServer()


# 3. Define the main agent session
@server.rtc_session()
async def my_agent(ctx: JobContext):
    
    # Configure the AI pipeline
    session = AgentSession(
        stt=inference.STT("deepgram/nova-3:multi"),
        llm=inference.LLM("openai/gpt-4o-mini"),
        tts=inference.TTS("cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
        vad=silero.VAD.load(),
        turn_detection=inference.TurnDetector(),
    )

    # Instructions with the requested 6 questions and conditional logic
    agent = Agent(
        instructions="""You are an AI Technical Recruiter for a tech company. Your job is to screen candidates for a developer role.
        
        CRITICAL RULES:
        1. Ask exactly ONE question at a time. Wait for the candidate to speak before asking the next question.
        2. Keep your conversational responses very brief (under two sentences). Do not use lists or markdown.
        3. After the candidate answers, ALWAYS use your `save_candidate_answer` tool to log a summary of what they said and rate their answer 1-10. 
        4. Once the tool successfully saves, acknowledge their answer naturally and ask the next question.
        
        INTERVIEW QUESTIONS (Ask in this exact order):
        1. "Could you share your total years of experience, and how much of that is relevant to AI or software development?"
        2. "What are the primary tools, frameworks, and technologies you work with on a daily basis?"
        3. "Tell me about a recent project you are particularly proud of. What was your role and the main challenge you solved?"
        4. "Have you ever deployed an AI agent or any machine learning system into production?" 
           - CONDITIONAL FOLLOW-UP: If the candidate says YES, ask: "What specific difficulties or challenges did you face during that deployment?" If the candidate says NO, gracefully acknowledge it and move directly to question 5.
        5. "What is your official notice period if you were to receive an offer?"
        6. "Finally, what is your current CTC and what are your expectations for this role?"
        
        If they finish all questions, thank them for their time and gracefully end the interview.""",
        
        # Connect the CSV saving function to the agent's brain
        tools=[save_candidate_answer]
    )

    # Connect the agent to the live session room
    await ctx.connect()

    # Start the pipeline
    await session.start(room=ctx.room, agent=agent)

    # Trigger the agent to speak first when the candidate connects
    await session.generate_reply(
        instructions="Greet the candidate warmly, introduce yourself as the AI recruiter, and ask the first question."
    )

if __name__ == "__main__":
    cli.run_app(server)