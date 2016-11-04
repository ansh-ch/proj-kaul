#include<stdio.h>
#include<string.h>
#include<unistd.h>
#include<stdlib.h>
#include<sys/types.h>
#include<sys/ptrace.h>
#include<sys/stat.h> 
#include <fcntl.h>
#include<signal.h>
#define link struct link

link
{
  pid_t id;
  int what;
  char name[50];
  int jno;
  link *next;
};
link *P=NULL;
int no_glo=0;
pid_t parent,foreson,gparent;
char forename[30];

void add(pid_t pid,int bg,char *cmd)
{
  link *p=P;
  if(p==NULL)
    {
      p=(link *)malloc(sizeof(link));
      p->next=NULL;
      p->id=pid;
      p->what=bg;
      no_glo+=1;
      p->jno=no_glo;
      strcpy(p->name,cmd);
      P=p;
    }
  else
    {
      while(p->next!=NULL)
	{
	  p=p->next;
	}
      link *t=(link *)malloc(sizeof(link));
      t->next=NULL;
      t->id=pid;
      t->what=bg;
      no_glo+=1;
      t->jno=no_glo;
      strcpy(t->name,cmd);
      p->next=t;
    }
}

void delete(pid_t pid)
{
  link *p=P;
  link *t=NULL;
  if(p!=NULL && p->id==pid)
    {
      P=P->next;
      if(p->what==1)
	printf("%d removed\n",pid);
    }
  else if(p!=NULL)
    {
      t=P;
      p=p->next;
      while(p!=NULL)
	{
	  if(p->id==pid)
	    {
	      t->next=p->next;
	      if(p->what==1)
		printf("\n%d removed\n",pid);
	      p=NULL;
	      break;
	    }
	  p=p->next;
	  t=t->next;
	}
    }
}

char **split_this(char *line,char *delim)
{
  int i=0,bsize=64;
  char**args=malloc(bsize*sizeof(char*));
  char *arg;


  arg=strtok(line,delim);
  while(arg)
    {
      args[i++]=arg;
      arg=strtok(NULL,delim);
    }
  args[i]=NULL;
  return args;
}

char home[1000];

int cd(char **args)
{
  if(chdir(args[1])!=0)
    perror("ERROR: ");
  return 1;
}

int xpwd(char **args)
{
  char temp[1000];
  getcwd(temp,1000);
  puts(temp);
  return 1;
}

int quit(char **args)
{
  _exit(0);
}

int xecho(char **args)
{
  char s[1000],sf[1000];
  int i=1,j=0,n=0,e=0,E=0,temp,flag=0,count=0,count1=0;
  while(args[i]!=NULL)
    {
      if(args[i][0]=='-')
	for(j=1;args[i][j]!='\0';j++)
	  {
	    if(args[i][j]=='n')
	      n=1;
	    else if(args[i][j]=='e')
	      {e=1;E=0;}
	    else if(args[i][j]=='E')
	      {E=1;e=0;}
	  }
      else
	if(flag==0)
	  {temp=i;flag=1;break;}
      i++;
    }
  strcpy(s,args[temp++]);
  while(args[temp]!=NULL)
    {
      strcat(s," ");
      strcat(s,args[temp++]);
    }

  int len=strlen(s);
  i=0;j=0;flag=0;
  for(i=0;i<=len;i++)
    {
      if(s[i]!='\\' || flag==1)
	{
	  sf[j++]=s[i];
	  if(s[i]=='"' && flag==0)
	    count++;
	  else if(s[i]=='\'' && flag==0)
	    count1++;
	  flag=0;
	  continue;
	}
      if(s[i]=='\\')
	flag=1;
    }
  sf[j]='\0';
  temp=0;
  if(count %2==1 || count1 %2==1)
    temp=1;
  if(n!=1 && temp==0)
    printf("%s\n",sf);
  else if(temp==0)
    printf("%s",sf);
  else if(temp==1)
    perror("FAILURE leads to ");
  return 1;
}

int kjob(char* s,char *r)
{
  pid_t pid;
  int sig=atoi(r);
  int find=atoi(s);
  link *p=P;
  while(p!=NULL)
    {
      if(p->jno==find)
	{kill(p->id,SIGKILL);break;}
      p=p->next;
    }
  return 1;
}

int overkill()
{
  link *p=P;
  while(p!=NULL)
    {
      if(p->what==1)
	{kill(p->id,SIGKILL);}
      p=p->next;
    }
  return 1;
}

int jobs()
{
  link *p=P;
  printf("\n");
  while(p!=NULL)
    {
      if(p->what==1)
	printf("[%d]  %s  %d\n",p->jno,p->name,p->id);
      p=p->next;
    }
  return 1;
}

void ctrlz()
{
  if(foreson!=parent)
    {
      add(foreson,1,forename);
      kill(foreson,SIGSTOP);
    }
}

int fg(char *s)
{
  int find=atoi(s);
  link *p=P;
  char get_name[30];
  pid_t pid;
  while(p!=NULL)
    {
      if(p->jno==find)
	{pid=p->id;strcpy(get_name,p->name);break;}
      p=p->next;
    }
  
  delete(pid);
  foreson=pid;
  strcpy(forename,get_name);
  kill(pid,SIGCONT);
  // signal(SIGTSTP,ctrlz);
  waitpid(foreson,NULL,WUNTRACED);
}

char *custom_str[] = {
  "cd",
  "xpwd",
  "quit",
  "xecho"
};    

int (*custom_func[]) (char **) = {
  &cd,
  &xpwd,
  &quit,
  &xecho
};

void deal_wt_it()
{
  int status;
  pid_t pid;
  pid=waitpid(-1,&status,WNOHANG);
  delete(pid);
}

int nocnoc(char**args)
{
  int flag=0;
  pid_t pid;
  pid=fork();
  add(pid,1,args[0]);
  signal(SIGCHLD,deal_wt_it);
  if(pid<0)
     perror("child fork not created");  
  else if(pid==0)
    {
      setpgid(0,0);
      if(execvp(args[0],args)==-1)
	{delete(getpid());perror("cmd couldnt be executed");}      
    }
  else
    {
      tcsetpgrp(0,getpgrp());
    }
  return 1;
}

int perfect(char **args)
{
  pid_t pid;
  pid=fork();
  foreson=pid;
  strcpy(forename,args[0]);
  if(pid<0)
     perror("child fork not created");
  else if(pid==0)
    {
      int take=0,give=0,i=1,j,t=0,g=0,v=0,fi=-1,fj=-1,flag=0;
      char taker[100],giver[100];
      
      while(args[i]!=NULL)
	{
	  for(j=0;args[i][j]!='\0';j++)
	    {
	      if(args[i][j]=='<')
		{
		  take=1;if(give==0){fi=i;fj=j;}
		}
	      if(args[i][j]=='>')
		{
		  if(take==0)
		    {if(give!=1){fi=i;fj=j;}}
		  give=1;
		}

	      if(take==1)
		{
		  if(args[i][j]=='>')
		    take=2;
		  else
		    if(args[i][j]!='<')
		      taker[t++]=args[i][j];
		  if(args[i][j+1]=='>'||(args[i][j+1]=='\0' && args[i+1]==NULL))
		    take=2;
		}
	      if(give==1)
		{
		  if(args[i][j]=='<')
		    give=2;
		  else
		    if(args[i][j]!='>')
		      giver[g++]=args[i][j];
		    else
		      if(args[i][j+1]=='>')
			flag=1;
		  if(args[i][j+1]=='<'||(args[i][j+1]=='\0' && args[i+1]==NULL))
		    give=2;
		}
	    }
	  i++;
	}
      taker[t]='\0';
      giver[g]='\0';
      //      printf("taker:%s giver:%s\n",taker,giver);
      
      take=give=0;
      if(fi>0||fj>=0)
	{
	  if(strlen(args[fi])>1 && fj!=0)
	    {
	      args[fi][fj]='\0';
	      args[fi+1]=NULL;
	    }
	  else
	    args[fi]=NULL;
	}
      if(strlen(taker)>0)
	{take=open(taker,O_RDONLY);dup2(take,0);close(take);}
      if(strlen(giver)>0)
	{
	  if(flag==0)
	    give=open(giver, O_RDONLY|O_WRONLY|O_CREAT,S_IRWXU);
	  else
	    give=open(giver, O_RDWR|O_APPEND|O_CREAT,S_IRWXU);
	  dup2(give,1);
	  close(give);
	}
      if(execvp(args[0],args)==-1)
	perror("cmd couldnt be executed ");
    }
  waitpid(0,NULL,WUNTRACED);
  foreson=parent;
  fflush(stdout);
  return 1;
}

int mpipe(char **args)
{
  int fd[2],tf=0,i=0;
  pid_t pid;
  char **temp;
  while(args[i]!=NULL)
    {
      temp=split_this(args[i]," \t\n");
      pipe(fd);
      pid=fork();
      if(pid<0)
	perror("child fork not created");
      else if(pid==0)
	{
	  //	  foreson=getpid();
	  close(fd[0]);
	  
	  int take=0,give=0,h=0,j=0,t=0,g=0,v=0,fi=-1,fj=-1,flag=0;
	  char taker[100],giver[100];
	  
	  while(temp[h]!=NULL)
	    {
	      for(j=0;temp[h][j]!='\0';j++)
		{
		  if(temp[h][j]=='<')
		    {
		      take=1;fi=h;fj=j;
		    }

		  if(take==1)
		    {
		      if(temp[h][j]!='<')
			{taker[t++]=temp[h][j];}
		      if((temp[h][j+1]=='\0' && temp[h+1]==NULL))
			take=2;
		    }
		}
	      h++;
	    }
	  taker[t]='\0';take=0;
	  
	  if(args[i+1]!=NULL)
	    dup2(fd[1],1);
	  else
	    {
	      h=0;
	      while(temp[h]!=NULL)
		{
		  for(j=0;temp[h][j]!='\0';j++)
		    {
		      if(temp[h][j]=='>')
			{
			  if(give!=1)
			    {fi=h;fj=j;}
			  give=1;
			}

		      if(give==1)
			{
			  if(temp[h][j]!='>')
			    {giver[g++]=temp[h][j];}
			  else
			    if(temp[h][j+1]=='>')
			      flag=1;
			  if((temp[h][j+1]=='\0' && temp[h+1]==NULL))
			    give=2;
			}
		    }
		  h++;
		}
	    }
	  giver[g]='\0';give=0;

	  if(fi>0||fj>=0)
	    {
	      if(strlen(temp[fi])>1 && fj!=0)
		{
		  temp[fi][fj]='\0';
		  temp[fi+1]=NULL;
		}
	      else
		temp[fi]=NULL;
	    }
	  if(strlen(giver)>0 && args[i+1]==NULL)
	    {
	      if(flag==0)
		give=open(giver, O_RDONLY|O_WRONLY|O_CREAT,S_IRWXU);
	      else
		if(flag==1)
		  give=open(giver, O_RDWR|O_APPEND|O_CREAT,S_IRWXU);
	      dup2(give,1);
	      close(give);
	    }

	  if(strlen(taker)>0)
	    {take=open(taker,O_RDONLY);dup2(take,0);close(take);}
	  else
	    dup2(tf,0);
	  if(execvp(temp[0],temp)==-1)
	    perror("Exec error ");
	  _exit(0);
	}
      else if(pid>0)
	{
	  int status;
	  wait(NULL);
	  foreson=parent;
	  close(fd[1]);
	  tf=fd[0];
	}
      
      i++;
    }
  return 1;
}


int cmd_execute(char **args)
{
  signal(SIGCHLD,deal_wt_it);
  signal(SIGTSTP,ctrlz);
  if(args[0]==NULL)
    return 1;
  int i=0,custom_size=sizeof(custom_str)/sizeof(char*);
  custom_size=3;
  for(i=0;i<=custom_size;i++)
    {
      if (strcmp(args[0], custom_str[i]) == 0)
	return (*custom_func[i])(args);
    }
  if(strcmp(args[0],"kjob")==0)
    {
      if(args[1]!=NULL && args[2]!=NULL)
	return kjob(args[1],args[2]);
      else 
	{printf("Invalid Arguments\n");return 1;}
    }
  if(strcmp(args[0],"overkill")==0)
    return overkill();
  if(strcmp(args[0],"jobs")==0)
    return jobs();
  if(strcmp(args[0],"fg")==0)
    return fg(args[1]);
  int what=-1,why=-1;
  i=0;
  while(args[i]!=NULL)
    {
      if(args[i+1]==NULL)
	{
	  int ha;
	  for(ha=0;args[i][ha]!='\0';ha++)
	      if(args[i][ha]=='&')
		{what=i;why=ha;}
	}
      i++;
    }
  if(what>=0)
    {
      if(why>0)
       	{args[what][why]='\0';args[what+1]=NULL;}
      else
	args[what]=NULL;
      return nocnoc(args);
    }
  
  return perfect(args);
}

char *cut_it(char str[],int len)
{
  int i,j=0;
  char *s;
  s=(char*)malloc(sizeof(char)*1000);
  for(i=len;str[i];i++)
    {
      s[j++]=str[i];
    }
  s[j]='\0';
  return s;
}

void start_loop()
{
  char *line;
  char **cmd;
  char **args,**gargle;
  int status,i;
  size_t bytes=0;
  parent=getpid();
  foreson=parent;
  gparent=getpgid(parent);

  char name[100];
  name[99]='\0';
  gethostname(name,99);
  getcwd(home,1000);
  int len=strlen(home);
  do
    {
      char *temp,str[1000];
      temp=(char*)malloc(sizeof(char)*1000);
      signal(SIGINT,SIG_IGN);

      getcwd(str,1000);

      if(strlen(str)>=strlen(home))
       	{
	  temp=cut_it(str,len);
	  printf("%s:~%s > ",name,temp);
      	}
      else
        printf("%s:%s > ",name,str);
      line=NULL;
      getline(&line,&bytes,stdin);
      cmd=split_this(line,";");
      i=0;
      while(cmd[i]!=NULL)
	{
	  int j=0;
	  status=1;
	  args=split_this(cmd[i],"|");
	  if(args[1]==NULL)
	    {
	      args=split_this(cmd[i]," \t\n");
	      status=cmd_execute(args);
	    }
	  else
	    mpipe(args);
	  i++;
	}
    }while(status!=0);
  free(args);
}      

int main(int argc,char **argv)
{
  //  signal(SIGTSTP,SIG_IGN);
  start_loop();
  return 0;
}
