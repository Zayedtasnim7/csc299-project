def summarize_task(description):
    """Mock summarizer - uses simple rules instead of API"""
    words = description.split()
    if 'research' in description.lower() or 'paper' in description.lower():
        return 'Complete research paper'
    elif 'grocery' in description.lower() or 'store' in description.lower():
        return 'Buy groceries'
    elif 'homework' in description.lower():
        return 'Finish homework assignment'
    else:
        # Take first 3-4 meaningful words
        meaningful = [w for w in words[:10] if len(w) > 3][:3]
        return ' '.join(meaningful).capitalize()

def main():
    # Sample task descriptions
    tasks = [
        'I need to finish writing my research paper on climate change impacts in coastal cities. This includes gathering the latest data from scientific journals, analyzing trends over the past decade, creating visualizations, and writing a comprehensive conclusion section. The paper should be at least 15 pages and follow APA format.',
        'Go to the grocery store and buy ingredients for dinner tonight. Need to get chicken breast, fresh vegetables like broccoli and carrots, pasta, olive oil, garlic, and parmesan cheese. Also pick up some dessert items and maybe some snacks for the week.',
        'Complete all the homework assignments for CSC299 including tasks1 through tasks5, record a demo video, and write a comprehensive summary of the development process.'
    ]
    
    print('=== Task Summarizer ===\n')
    
    for i, task_desc in enumerate(tasks, 1):
        print(f'Task {i}:')
        print(f'Description: {task_desc[:80]}...')
        summary = summarize_task(task_desc)
        print(f'Summary: {summary}\n')

if __name__ == '__main__':
    main()
