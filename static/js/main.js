document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('events-container');
    const template = document.getElementById('event-template');
    const emptyState = document.getElementById('empty-state');

    let lastEventCount = -1;

    async function pollEvents() {
        try {
            const response = await fetch('/api/events');
            const events = await response.json();

            // Show/hide empty state
            if (events.length === 0) {
                emptyState.style.display = 'block';
                container.style.display = 'none';
                return;
            } else {
                emptyState.style.display = 'none';
                container.style.display = 'flex';
            }

            // Only re-render if event count changed (simple optimization)
            if (events.length === lastEventCount) {
                return;
            }
            lastEventCount = events.length;

            // Clear container
            container.innerHTML = '';

            events.forEach(event => {
                const clone = template.content.cloneNode(true);
                const card = clone.querySelector('.event-card');

                // Set type class for styling
                card.classList.add(`type-${event.action}`);

                // Icon based on type
                const iconDiv = clone.querySelector('.event-icon');
                if (event.action === 'PUSH') iconDiv.textContent = '⬆';
                if (event.action === 'PULL_REQUEST') iconDiv.textContent = '⤴';
                if (event.action === 'MERGE') iconDiv.textContent = '⪢';

                // Content
                const message = formatEventMessage(event);

                clone.querySelector('.event-author').textContent = event.author;
                clone.querySelector('.event-action').textContent = event.action.replace('_', ' ');
                clone.querySelector('.event-message').textContent = message;

                // Repo badge
                const repoEl = clone.querySelector('.event-repo');
                if (repoEl && event.repo) {
                    repoEl.textContent = event.repo;
                }

                // Branch info
                let branchInfo = '';
                if (event.action === 'PUSH') {
                    branchInfo = `${event.to_branch}`;
                } else if (event.from_branch && event.to_branch) {
                    branchInfo = `${event.from_branch} → ${event.to_branch}`;
                }
                clone.querySelector('.event-branches').textContent = branchInfo;

                // Time
                clone.querySelector('.event-time').textContent = event.timestamp;

                container.appendChild(clone);
            });

        } catch (error) {
            console.error('Error fetching events:', error);
        }
    }

    function formatEventMessage(event) {
        if (event.action === 'PUSH') {
            return `Pushed to ${event.to_branch}`;
        } else if (event.action === 'PULL_REQUEST') {
            return `Submitted a pull request from ${event.from_branch} to ${event.to_branch}`;
        } else if (event.action === 'MERGE') {
            return `Merged branch ${event.from_branch} to ${event.to_branch}`;
        }
        return 'Unknown action';
    }

    // Initial load
    pollEvents();

    // Poll every 15 seconds
    setInterval(pollEvents, 15000);
});
