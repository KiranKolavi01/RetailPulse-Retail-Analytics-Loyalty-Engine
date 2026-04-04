"""
run_pipeline.py — RetailPulse Run Pipeline Page
Source: RETAILPULSE_FRONTEND.md Page 1 — Run Pipeline.
"""
import streamlit as st


def render():
    from custom_styles import apply_theme, section_header, show_success, show_error
    from client import RetailPulseClient
    from config import BASE_URL

    apply_theme()
    section_header("Run Pipeline")
    st.markdown("Trigger the full RetailPulse data pipeline from ingestion to dashboard generation.")
    st.divider()

    client = RetailPulseClient(BASE_URL)

    # Initialize pipeline state
    if "pipeline_running" not in st.session_state:
        st.session_state["pipeline_running"] = False
    if "pipeline_logs" not in st.session_state:
        st.session_state["pipeline_logs"] = []
    if "pipeline_done" not in st.session_state:
        st.session_state["pipeline_done"] = False
    if "pipeline_error" not in st.session_state:
        st.session_state["pipeline_error"] = None

    # Show previous logs if any
    if st.session_state["pipeline_logs"]:
        st.markdown("**Pipeline Log:**")
        for log_line in st.session_state["pipeline_logs"]:
            st.markdown(log_line)

    if st.session_state["pipeline_done"]:
        show_success("All pipeline steps completed successfully.")

    if st.session_state["pipeline_error"]:
        show_error(st.session_state["pipeline_error"])

    # Run button — disabled while running
    run_clicked = st.button(
        "Run Full Pipeline",
        key="run_pipeline_btn",
        disabled=st.session_state["pipeline_running"],
    )

    if run_clicked:
        st.session_state["pipeline_running"] = True
        st.session_state["pipeline_logs"] = []
        st.session_state["pipeline_done"] = False
        st.session_state["pipeline_error"] = None

        steps = [
            "Step 1: Setup DB",
            "Step 2: ETL Pipeline",
            "Step 3: Loyalty & RFM",
            "Step 4: Predictive Analytics",
            "Step 5: Dashboard Generation",
        ]

        log_container = st.empty()
        progress_logs = []

        with st.spinner("Pipeline running..."):
            try:
                result = client.run_pipeline()

                # Parse step results from response
                # Backend may return {"steps": [...], "status": "success"} or similar
                if isinstance(result, dict):
                    returned_steps = result.get("steps", result.get("logs", []))
                    status = result.get("status", "success")
                    failed_step = result.get("failed_step", None)
                else:
                    returned_steps = []
                    status = "success"
                    failed_step = None

                # Display step-by-step logs
                for i, step_label in enumerate(steps):
                    if returned_steps and i < len(returned_steps):
                        step_info = returned_steps[i]
                        step_status = step_info.get("status", "success") if isinstance(step_info, dict) else "success"
                        step_msg = step_info.get("message", step_label) if isinstance(step_info, dict) else str(step_info)
                    else:
                        step_status = "success" if status == "success" else ("failed" if i == len(steps) - 1 else "success")
                        step_msg = step_label

                    if step_status in ("success", "completed", "done"):
                        progress_logs.append(f"✓ {step_msg}")
                    elif step_status in ("failed", "error"):
                        progress_logs.append(f"✗ {step_msg}")
                    else:
                        progress_logs.append(f"✓ {step_msg}")

                    with log_container.container():
                        for line in progress_logs:
                            st.markdown(line)

                st.session_state["pipeline_logs"] = progress_logs

                if status in ("failed", "error") or failed_step:
                    failed_name = failed_step or "unknown step"
                    st.session_state["pipeline_error"] = f"Pipeline failed at: {failed_name}"
                    st.session_state["pipeline_done"] = False
                else:
                    st.session_state["pipeline_done"] = True

            except Exception as e:
                err = str(e).lower()
                if "connection" in err or "refused" in err:
                    st.session_state["pipeline_error"] = (
                        "Cannot connect to backend. Is the FastAPI server running at the configured URL?"
                    )
                else:
                    st.session_state["pipeline_error"] = f"Pipeline failed: {str(e)}"
                st.session_state["pipeline_done"] = False

        st.session_state["pipeline_running"] = False
        st.rerun()
