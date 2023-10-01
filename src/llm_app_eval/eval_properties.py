import openai
from evaluator import EvalProperty, OutputFormat, PropertyResult, TestCase

property_llm = "gpt-3.5-turbo-0613"


def evaluate_property_with_llm(
    model: str, system_message: str, user_message: str
) -> PropertyResult:
    return openai.ChatCompletion.create(
        model=model,
        response_model=PropertyResult,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
    )


def factually_consistent(test_case: TestCase, llm_app_result: OutputFormat) -> PropertyResult:
    if test_case.reference_output and llm_app_result.answer:
        result = evaluate_property_with_llm(
            model=property_llm,
            system_message="Evaluate the answer. The answer should be factually consistent with the reference answer. If not, explain why.",
            user_message=f"Answer: {llm_app_result.answer}\nReference Answer: {test_case.reference_output.answer}",
        )
    else:
        result = None
    return result


def improves_historical_answer(test_case: TestCase, llm_app_result: OutputFormat) -> PropertyResult:
    if test_case.test_input and test_case.historical_output and llm_app_result.answer:
        result = evaluate_property_with_llm(
            model=property_llm,
            system_message="Evaluate the new answer. Is the new answer better than the old answer? Explain why.",
            user_message=f"Question: {test_case.test_input.question}\nOld answer: {test_case.historical_output.answer}\nNew answer: {llm_app_result.answer}",
        )
    else:
        result = None
    return result


def takes_feedback_into_account(
    test_case: TestCase, llm_app_result: OutputFormat
) -> PropertyResult:
    if (
        test_case.test_input
        and test_case.historical_output
        and llm_app_result.answer
        and test_case.historical_feedback
    ):
        result = evaluate_property_with_llm(
            model=property_llm,
            system_message="Evaluate the new answer. Does the new answer improve upon the old one by taking the feedback into account? Explain why.",
            user_message=f"Question: {test_case.test_input.question}\nOld answer: {test_case.historical_output.answer}\nOld feedback: {test_case.historical_feedback}\nNew answer: {llm_app_result.answer}",
        )
    else:
        result = None
    return result


def length_within_bounds(test_case: TestCase, llm_app_result: OutputFormat) -> PropertyResult:
    if test_case.reference_output and llm_app_result.answer:
        if len(llm_app_result.answer) <= 1.2 * len(test_case.reference_output.answer):
            result = PropertyResult(feedback="The answer is not too long.", pass_fail=True)
        else:
            result = PropertyResult(feedback="The answer is too long.", pass_fail=False)
    else:
        result = None
    return result


properties = [
    EvalProperty(
        property_name="FactuallyConsistent",
        description="The answer is factually consistent with the reference answer.",
        eval_func=factually_consistent,
    ),
    # EvalProperty(
    #     property_name="CorrectLanguage"
    #     description="The answer is in the same language as the question.",
    # ),
    EvalProperty(
        property_name="ImprovesHistoricalAnswer",
        description="The answer improves upon the historical answer. It is more complete, more concise, or more accurate.",
        eval_func=improves_historical_answer,
    ),
    EvalProperty(
        property_name="TakesFeedbackIntoAccount",
        description="The answer improves upon the historical answer by taking the feedback into account.",
        eval_func=takes_feedback_into_account,
    ),
    EvalProperty(
        property_name="LengthWithinBounds",
        description="The answer is max 20% longer than the reference answer.",
        eval_func=length_within_bounds,
    ),
]