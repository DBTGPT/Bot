import logging
import sys
import os
from openai import OpenAI
import tiktoken

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

sys.path.append(os.path.join(sys.path[0], '../..'))

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
logger = logging.getLogger('sim_thread')
logger.setLevel(logging.INFO)

MODEL_DEPLOYMENT = os.getenv('MODEL_DEPLOYMENT', 'gpt-4')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
assert OPENAI_API_KEY is not None, 'OpenAI API Key must be present in env variables'

class SimThread:
    def __init__(
            self,
            client: OpenAI,
            dbt_system_prompt: str = '',
            dbt_initial_msg: str = None, 
            persona_system_prompt: str = '',
            persona_initial_msg: str = None, 
            initiator: str = 'dbt',
            thread_msg_limit: int = 10,
            thread_token_length_limit: int = 10000,
        ):
        logger.info("Initializing SimThread")
        self.client = client
        self.token_encoder = tiktoken.get_encoding('cl100k_base')

        self.dbt_info = {
            'system_prompt': dbt_system_prompt,
            'init_msg': dbt_initial_msg,
        }
        self.persona_info = {
            'system_prompt': persona_system_prompt,
            'init_msg': persona_initial_msg,
        }
        self.stats_keys = self._init_stats().keys()
        self.dbt_info.update(self._init_stats())
        self.persona_info.update(self._init_stats())
        self.agent_name_map = {
            'dbt': {'console': '___BerkeleyDBT___', 'eval': 'Therapist'},
            'persona': {'console': '___  Persona  ___', 'eval': 'Client'},
        }

        self.thread_msgs = []
        self.thread_msg_limit = thread_msg_limit
        self.thread_token_length_limit = thread_token_length_limit
        self.thread_stats = self._init_stats()

        self._chk_invalid_agent(initiator)
        self.initiator = initiator
        self.next_to_respond = initiator

    @staticmethod
    def _init_stats():
        return {
            'n_msgs': 0,
            'n_msgs_generated': 0,
            'token_length': 0,
            'tokens_processed': 0,
            'tokens_prompted': 0,
            'tokens_completed': 0,
            'est_processing_cost': 0.0,
            'est_prompting_cost': 0.0,
            'est_completion_cost': 0.0,
        }

    def _calc_thread_stats(self):
        logger.info("Calculating thread stats")
        for key in self.stats_keys:
            self.thread_stats[key] = self.dbt_info[key] + self.persona_info[key]
        return self.thread_stats

    def _update_agent_costs(self, agent: str):
        logger.info(f"Updating costs for agent: {agent}")
        agent_info = self.get_agent_info(agent)
        agent_info['est_prompting_cost'] = 0.01 * agent_info['tokens_prompted'] / 1000
        agent_info['est_completion_cost'] = 0.03 * agent_info['tokens_completed'] / 1000
        agent_info['est_processing_cost'] = agent_info['est_prompting_cost'] + agent_info['est_completion_cost']

    @staticmethod
    def _chk_invalid_agent(agent: str):
        if agent not in ['dbt', 'persona']:
            logger.error(f'Invalid agent: {agent}')
            raise Exception(f'{agent} is not \'dbt\' or \'persona\'')

    def count_tokens(self, msg: str):
        return len(self.token_encoder.encode(msg))

    def get_agent_info(self, agent: str):
        if agent == 'dbt':
            return self.dbt_info
        return self.persona_info

    def _switch_responder(self):
        logger.info("Switching responder")
        if self.next_to_respond == 'dbt':
            self.next_to_respond = 'persona'
        else:
            self.next_to_respond = 'dbt'

    def _chk_within_limits(self):
        return (
            self.thread_stats['n_msgs'] < self.thread_msg_limit
            and self.thread_stats['token_length'] < self.thread_token_length_limit
        )

    def _vprint_msg(self, msg: dict, verbose=False):
        if not verbose:
            return
        print(self.msg_to_console(msg), end='\n\n')

    def msg_to_console(self, msg: dict):
        agent = msg['role']
        msg_txt = msg['content']
        agent_console_name = self.agent_name_map[agent]['console']
        return f'{agent_console_name}\n{msg_txt}'

    def msg_to_eval(self, msg: dict):
        agent = msg['role']
        agent_eval_name = self.agent_name_map[agent]['eval']
        msg_txt = msg['content']
        return f'{agent_eval_name}: {msg_txt}'

    def msgs_to_console(self):
        return '\n\n'.join([self.msg_to_console(msg) for msg in self.thread_msgs])

    def msgs_to_eval(self):
        return '\n\n'.join([self.msg_to_eval(msg) for msg in self.thread_msgs])

    def get_msgs_from_pov(self, agent: str):
        agent_system_prompt = self.get_agent_info(agent).get('system_prompt')
        pov_msgs = []
        dummy_msg = []
        sys_msg = []

        for msg in self.thread_msgs:
            if msg['role'] == agent:
                pov_role = 'assistant'
            else:
                pov_role = 'user'
            pov_msgs.append({'role': pov_role, 'content': msg['content']})

        if not pov_msgs or (pov_msgs and pov_msgs[0]['role'] == 'assistant'):
            dummy_msg = [{'role': 'user', 'content': ''}]

        if agent_system_prompt:
            sys_msg = [{'role': 'system', 'content': agent_system_prompt}]

        return [*sys_msg, *dummy_msg, *pov_msgs]

    def next_response(self):
        agent_info = self.get_agent_info(self.next_to_respond)

        if agent_info.get('init_msg') and agent_info['n_msgs'] == 0:
            msg_txt = agent_info['init_msg']
            msg = {'role': self.next_to_respond, 'content': msg_txt}
            self.thread_msgs.append(msg)
            msg_tokens = self.count_tokens(msg_txt)
            agent_info['n_msgs'] += 1
            agent_info['token_length'] += msg_tokens
            logger.info(f"Initial message sent by {self.next_to_respond}: {msg_txt}")

        else:
            try:
                response = self.client.ChatCompletion.create(
                    model=MODEL_DEPLOYMENT,
                    messages=self.get_msgs_from_pov(self.next_to_respond)
                )
                msg_txt = response.choices[0].message['content']
                msg = {'role': self.next_to_respond, 'content': msg_txt}
                self.thread_msgs.append(msg)
                agent_info['n_msgs'] += 1
                agent_info['n_msgs_generated'] += 1
                agent_info['token_length'] += response.usage['completion_tokens']
                agent_info['tokens_processed'] += response.usage['total_tokens']
                agent_info['tokens_prompted'] += response.usage['prompt_tokens']
                agent_info['tokens_completed'] += response.usage['completion_tokens']
                logger.info(f"Message sent by {self.next_to_respond}: {msg_txt}")
            except Exception as e:
                logger.error(f"Error generating response for {self.next_to_respond}")
                logger.exception(e)
                raise

        self._update_agent_costs(self.next_to_respond)
        self._calc_thread_stats()
        self._switch_responder()
        return msg

    def run_thread(self, verbose=False):
        logger.info("Starting conversation thread")
        within_limits = self._chk_within_limits()
        while within_limits:
            self._vprint_msg(self.next_response(), verbose)
            within_limits = self._chk_within_limits()
        logger.info("Conversation thread completed")

    def extend_thread(self, n_msgs: int, verbose=False):
        logger.info(f"Extending conversation thread by {n_msgs} messages")
        assert n_msgs > 0
        for i in range(n_msgs):
            self._vprint_msg(self.next_response(), verbose)