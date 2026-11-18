from .nodes import WaitForTrigger, NavigateTo, DetectTarget, ExecuteGrasp, SpeakTTS

NODE_REGISTRY = {
    "WaitForTrigger": WaitForTrigger,
    "NavigateTo": NavigateTo,
    "DetectTarget": DetectTarget,
    "ExecuteGrasp": ExecuteGrasp,
    "SpeakTTS": SpeakTTS,
}