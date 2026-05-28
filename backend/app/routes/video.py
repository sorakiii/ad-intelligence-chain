@bp.route('/create_video', methods=['POST'])
def create_video():
    data = request.get_json()
    role_id = data.get('role_id')
    
    if role_id == 3:  # 视频脚本角色
        script_json = parse_script_to_json(data.get('content'))
        prompts = convert_script_to_prompts(script_json)
        
        tasks = []
        for prompt_data in prompts:
            task = VideoTask(
                prompt=prompt_data["prompt"],
                script_data=prompt_data["script_data"],  # 现在是字符串
                status=TaskStatus.PENDING
            )
            db.session.add(task)
            tasks.append(task)
        
        try:
            db.session.commit()
            # 为每个任务启动异步处理
            for task in tasks:
                create_video_task.delay(task.id)
            
            return jsonify({
                'status': 'success',
                'message': f'Created {len(tasks)} video tasks',
                'task_ids': [task.id for task in tasks]
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    # 处理其他角色...