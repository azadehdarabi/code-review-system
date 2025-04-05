import ast
import os
import httpx
import astor
from typing import List, Optional
from .config import Settings

settings = Settings()


async def find_function_in_module(module_path: str, function_name: str) -> Optional[str]:
    """
    Find and extract a function definition from a Python module.
    """
    try:
        with open(module_path, 'r') as file:
            content = file.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return astor.to_source(node)  # Extract function source safely

        return None
    except Exception as e:
        raise Exception(f"Error finding function: {str(e)}")


async def find_function_in_repo(repo_path: str, function_path: str) -> Optional[str]:
    """
    Find a function in a repository given its path (e.g., 'module_name.function_name').
    """
    try:
        # Split the function path into module and function name
        *module_parts, function_name = function_path.split('.')
        module_path = os.path.join(repo_path, *module_parts) + '.py'

        if not os.path.exists(module_path):
            module_init_path = os.path.join(repo_path, *module_parts, '__init__.py')
            if os.path.exists(module_init_path):
                module_path = module_init_path
            else:
                raise Exception(f"Module not found: {module_path}")

        if not os.path.exists(module_path):
            raise Exception(f"Module not found: {module_path}")

        return await find_function_in_module(module_path, function_name)
    except Exception as e:
        raise Exception(f"Error finding function in repo: {str(e)}")


async def analyze_function(job_id: str, function_name: str) -> List[str]:
    """
    Analyze a function from a previously downloaded repository.
    """
    try:
        # Construct the path to the repository
        repo_path = os.path.join(settings.repo_storage_path, job_id)

        if not os.path.exists(repo_path):
            raise Exception(f"Repository not found for job_id: {job_id}")

        # Find the function in the repository
        function_code = await find_function_in_repo(repo_path, function_name)

        if not function_code:
            raise Exception(f"Function not found: {function_name}")

        # Send the function code to the LLM service for analysis
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.llm_service_url}/analyze",
                json={"function_code": function_code}
            )

            if response.status_code != 200:
                raise Exception("Failed to get analysis from LLM service")

            result = response.json()
            return result["suggestions"]

    except Exception as e:
        raise Exception(f"Error analyzing function: {str(e)}")
