# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db import models

# Create your models here.
class User_Org_Info(models.Model):
    user_id = models.BigIntegerField(primary_key=True,default=0)   #用户id
    user_name = models.CharField(max_length=255)                #用户登陆姓名
    user_fullname = models.CharField(max_length=255,blank=True)                #用户姓名全程
    avatar_url = models.CharField(max_length=500)               #头像地址
    follows_count = models.IntegerField(default=0)              #被关注数
    repos_count = models.IntegerField(default=1)                #项目数
    blog_url = models.CharField(max_length=500,blank=True,null=True)                 #bolg地址
    email_url = models.CharField(max_length=500,blank=True,null=True)                #emall地址
    belong_org = models.IntegerField(default=0,blank=True,null=True)               #所属组织
    org_member_count = models.IntegerField(default=0)           # 组织会员数
    user_type = models.CharField(max_length=100)                  #类别 0 user 1 org 存字符
    user_create_time = models.CharField(max_length=100,blank=True)
    user_update_time = models.CharField(max_length=100,blank=True)
    update_time = models.DateTimeField(auto_now=True)
class Org_Members_Info(models.Model):
    org = models.ForeignKey(User_Org_Info)
    member_id = models.IntegerField(default=0)
class Repo_Base_Info(models.Model):
    repo_id = models.IntegerField(primary_key=True,default=0)
    repo_name = models.CharField(max_length=255)
    repo_full_name = models.CharField(max_length=255)
    repo_description = models.TextField(blank=True)                         #项目描述
    fork_count = models.IntegerField(default=0)                 #fork数量
    star_count = models.IntegerField(default=0)                 #收藏数量
    subscribe_count = models.IntegerField(default=0)            #关注数量
    language = models.TextField(blank=True)                                  #所用语言 语言:数量（行）
    repo_created_time = models.CharField(max_length=100,blank=True)                    #项目创建时间
    repo_update_time = models.CharField(max_length=100,blank=True)      #项目最近更新时间
    repo_size = models.IntegerField(default=0)                  #repo大小
    owner_type = models.CharField(max_length=100,blank=True)                 #拥有者属性 0 user 1 org
    repo_owner = models.ForeignKey(User_Org_Info,default=0)
    update_time = models.DateTimeField(auto_now=True)
    repo_branch_count = models.IntegerField(default=0)          #分支数量
    collaborators_count = models.IntegerField(default=0)          #贡献者数量
class Repo_Develop_info(models.Model):
    repo = models.ForeignKey(Repo_Base_Info);                #关联的repoid
    commit_count = models.IntegerField(default=0)               #commit 数量
    commit_count_permonth = models.TextField(blank=True)        #commit 每月数量
    command_count = models.IntegerField(default=0)              #command 数量
    #command_count_permonth = models.TextField(blank=True)                   #command 每月数量
    issue_count  = models.IntegerField(default=0)               #issue 数量
    #issue_count_permonth = models.IntegerField(default=0)       #issue 每月数量
    issue_command_count = models.IntegerField(default=0)        #issue command 数量
    #issue_command_count_permonth = models.IntegerField(default=0)#issue commang 每月数量
    #stats/participation
    commit_count_perweek_lastyear = models.TextField(blank=True)           #过去一年每周commit数量
    #stats/code_frequency
    code_add_count_perweek = models.TextField(blank=True)                   #每周add代码行数
    code_delete_count_perweek = models.TextField(blank=True)                #每周delete代码行数
    update_time = models.DateTimeField(auto_now=True)

class Repo_Developer_info(models.Model):
    repo = models.ForeignKey(Repo_Base_Info)                 #关联repo_id
    user = models.ForeignKey(User_Org_Info)                  #关联组织用户id
    user_creat_time = models.CharField(max_length=100,blank=True)             #用户加入时间(第一次commit)
    user_last_update_time = models.CharField(max_length=100,blank=True)       #用户最后更新时间(最后一此commit))
    user_commit_count = models.IntegerField(default=0)                        #用户commit数量
    user_commit_count_perweek = models.TextField(blank=True)                #每周commit数量
    user_add_count_perweek = models.TextField(blank=True)                   #该用户每周add代码行数
    user_del_count_perweek = models.TextField(blank=True)                   #该用户每周delete代码数量
    update_time = models.DateTimeField(auto_now=True)

class Repo_Issue_info(models.Model):
    issue_id = models.IntegerField(primary_key=True,default=0)      #issue_id
    issue_number = models.IntegerField(default=0)               #issue_number
    repo = models.ForeignKey(Repo_Base_Info)                 #关联repo_id
    user = models.ForeignKey(User_Org_Info)                  #关联组织用户id
    issue_user_type = models.CharField(max_length=100,blank=True)            #issue用户类型 0 member 1 user
    issue_state = models.IntegerField(default=0)                #issue 状态 0 open 1 close
    issue_create_time = models.CharField(max_length=100,blank=True,null=True)                   #issue创建时间
    issue_update_time = models.CharField(max_length=100, blank=True,null=True)
    issue_close_time = models.CharField(max_length=100,blank=True,null=True)                       #issue关闭时间
    update_time = models.DateTimeField(auto_now=True)
    issue_comment_count = models.IntegerField(default=0)

class Repo_Issue_Comment_info(models.Model):
    issue = models.ForeignKey(Repo_Issue_info)
    repo = models.ForeignKey(Repo_Base_Info)  # 关联repo_id
    issue_comment_id = models.IntegerField(primary_key=True,default=0)
    issue_comment_author = models.ForeignKey(User_Org_Info)
    issue_comment_author_association =  models.CharField(max_length=100)
    issue_comment_created_at = models.CharField(max_length=100)
    issue_comment_body = models.TextField(blank=True)
    update_time = models.DateTimeField(auto_now=True)
class Repo_Commit_info(models.Model):
    repo = models.ForeignKey(Repo_Base_Info)  # 关联repo_id
    commit_user =  models.ForeignKey(User_Org_Info)                #commit提交着
    committer_user = models.ForeignKey(User_Org_Info,related_name='committer_user')               #committer
    commit_file_count = models.IntegerField(default=0)              #改动的文件数量
    commit_file_per = models.TextField(blank=True)                  #文件改动具体情况file:add,del

#/pulls?state=all
class Repo_Pulls_info(models.Model):
    pull_id = models.IntegerField(primary_key=True,default=0)                 #pull_id
    pull_number = models.IntegerField(default=0)                #pull_number
    repo = models.ForeignKey(Repo_Base_Info)                     # 关联repo_id
    pull_state = models.IntegerField(default=0)               #pullrequest状态 0 open 1close
    user = models.ForeignKey(User_Org_Info)                #pull的请求着
    pull_author_association =  models.CharField(max_length=100)
    pull_create_time = models.CharField(max_length=100,blank=True,null=True)
    pull_update_time = models.CharField(max_length=100,blank=True,null=True)
    pull_closed_time = models.CharField(max_length=100,blank=True,null=True)
    pull_merged_time = models.CharField(max_length=100,blank=True,null=True)
    pull_is_merged = models.IntegerField(default=0)             #是否merged 0 false 1 true
    #pull_commit_count = models.IntegerField(default=0)              #pull中的commit数量
    #pull_add_count = models.IntegerField(default=0)             #pull中add代码的数量
    #pull_del_count = models.IntegerField(default=0)             #pull中delete代码的数量
    #pull_changed_files = models.IntegerField(default=0)             #pull中change file的数量
    update_time = models.DateTimeField(auto_now=True)
class Repo_milestones_info(models.Model):
    repo = models.ForeignKey(Repo_Base_Info)  # 关联repo_id
    milestones_id = models.IntegerField(primary_key=True,default=0)
    milestones_title = models.CharField(max_length=255)             #里程碑标题
    milestones_creater = models.ForeignKey(User_Org_Info)           #里程碑创建者
    milestones_state = models.IntegerField(default=0)               #里程碑状态 0 open 1close
    milestones_create_time = models.CharField(max_length=100,blank=True,null=True)  # milestones创建时间
    milestones_close_time = models.CharField(max_length=100,blank=True,null=True)  # milestones关闭时间
    milestones_update_time = models.CharField(max_length=100,blank=True,null=True)  # milestones更新时间
    update_time = models.DateTimeField(auto_now=True)




