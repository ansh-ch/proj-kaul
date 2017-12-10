#include <mpi.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>

using namespace std;


int **alloc_Array(int rows, int cols)
{       
  int** arr= (int**)malloc(rows*sizeof(int*));
  int* data = (int*)malloc(rows*cols*sizeof(int));
  int i = 0;
        
  while (i < rows)
    {
      arr[i] = &(data[cols*i]);
      i++;
    }
        
  return arr;
}

void assignVector(int **array, vector <int> arow, int rows, int cols)
{
  for (int j = 0; j < cols; j++)
    {
      array[rows-1][j] = arow[j];
    }
}

void display(int **array, int rows, int cols)
{
  for (int i = 0; i < rows; i++)
    {
      for (int j = 0; j < cols; j++)
	cout<<array[i][j]<<" ";
      cout<<endl;
    }
}

string whatIs(int n)
{
  if (n == 1)
    return "\u25A0";
  else 
    return "\u25A1";
}

void zisplay(int **array, int rows, int cols)
{
  for (int i = 0; i < rows; i++)
    {
      for (int j = 0; j < cols; j++)
	cout<<whatIs(array[i][j])<<" ";
      cout<<endl;
    }
}


int leftAnswer(int **array, int the_row,int the_col,int rows,int cols)
{
  if (the_col > 0)
    return array[the_row][the_col-1];

  return 0;      
}

int rightAnswer(int **array, int the_row,int the_col,int rows,int cols)
{
  if(the_col < (cols - 1))
    return array[the_row][the_col+1];

  return 0;
}

int upAnswer(int **array, int the_row,int the_col,int rows,int cols)
{
  if(the_row > 0)
    return array[the_row - 1][the_col];

  return 0;

}

int downAnswer(int **array, int the_row,int the_col,int rows,int cols)
{
  if(the_row < (rows - 1))
    return array[the_row + 1][the_col];

  return 0;

}

int diagonals(int **array, int the_row,int the_col,int rows,int cols)
{
  int count = 0;
  if(the_row > 0 && the_col > 0)
    count += array[the_row-1][the_col-1];
  if(the_row < (rows - 1) && the_col < (cols - 1))
    count += array[the_row+1][the_col+1];
  if(the_row < (rows - 1) && the_col > 0)
    count += array[the_row + 1][the_col-1];
  if(the_row > 0 && the_col < (cols - 1))
    count += array[the_row-1][the_col+1];

  return count;

}

int decide_cell_life( int count, int cell)
{
  if (count < 2)
    return 0;
  if (count == 2)
    return cell;
  if (count ==3)
    return 1;
  if (count > 3)
    return 0;
}

int* apply_rules(int **array, int *temp, int the_row, int rows, int cols, int world_rank)
{
  //cout<<"#"<<world_rank<<" Entered"<<endl ;
  int count;

  for (int the_col = 0; the_col < cols; the_col++)
    {      
      count = 0;
      count = count + leftAnswer(array, the_row,the_col,rows,cols) +rightAnswer(array, the_row,the_col,rows,cols);
      count = count + upAnswer(array, the_row,the_col,rows,cols) +downAnswer(array, the_row,the_col,rows,cols);
      count = count + diagonals(array, the_row,the_col,rows,cols);
	
      temp[the_col] = decide_cell_life( count, array[the_row][the_col] );

      //cout<<"("<<the_row<<","<<the_col<<")  "<< decide_cell_life( count, array[the_row][the_col] ) << endl << endl;
      //cout<<"("<<the_row<<","<<the_col<<")  "<< leftAnswer(array, the_row,the_col,rows,cols) <<" " <<rightAnswer(array, the_row,the_col,rows,cols)<<" ";
      //cout<<upAnswer(array, the_row,the_col,rows,cols)<<" "<<downAnswer(array, the_row,the_col,rows,cols)<<endl<<endl;
    }
  return temp;
}


int main(int argc, char **argv)
{

  int world_size, world_rank, **Prime , steps = atoi(argv[1]);
  int master = 0, rows, cols;
  
  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
  MPI_Comm_size(MPI_COMM_WORLD, &world_size);

  if (world_rank == master)
    {
      
      vector <int> arow;
      ifstream fin("linput.txt");
      int flag = 0;
      string str;
      rows = 0;
      
      while(getline(fin, str))
	{
	  cols = 0;
	  
	  for(int i = 0; i < str.length(); i++)
	    {
	      arow.push_back(str[i] - '0');
	      cols++;
	    }
	  rows++;

	  if (flag==0)
	    {
	      Prime = alloc_Array(cols,cols);	      
	      flag = 1;
	    }
	  
	  assignVector(Prime, arow, rows, cols);

	  /*for(vector <int>::iterator it = arow.begin(); it != arow.end(); it++)
	    cout<<*it<< " ";*/

	  arow.clear();
	}
      
      fin.close();     
    }

  MPI_Bcast(&rows,1,MPI_INT,master,MPI_COMM_WORLD);
  MPI_Bcast(&cols,1,MPI_INT,master,MPI_COMM_WORLD);

  if(world_rank != master)
    {
      Prime = alloc_Array(rows,cols);
    }

  MPI_Barrier(MPI_COMM_WORLD);
  
  while(steps)
    {

      MPI_Bcast(&Prime[0][0], rows*cols, MPI_INT, master, MPI_COMM_WORLD);

      if (world_rank == master)
	{
	  int *temp = (int *)malloc(cols*sizeof(int));
	  for(int i = 0; i<rows; i++)
	    {

	      if (i % world_size != master)
		MPI_Send(&i, 1, MPI_INT, i % world_size, 0, MPI_COMM_WORLD);

	      else
		{
		  temp = apply_rules(Prime, temp, i, rows, cols, world_rank);
		  for(int z = 0; z < cols; z++ )
		    {
		      Prime[i][z] = temp[z];
		    }
		}
	      
	    }
	  
	  for(int i = 0; i<rows; i++)
	    {
	      if (i % world_size != master)
		MPI_Recv(Prime[i], cols, MPI_INT, i % world_size, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
	    }

	  zisplay(Prime, rows, cols);
	  cout<<endl;
	}

      
      else
	{	
	  int **temp = NULL;
	  int count_rows = rows/world_size;
	  int select_row = -1;
	  
	  //cout<<"Pt4 "<<world_rank<< " count_rows = "<<count_rows<<endl;
	  if (rows % world_size >= world_rank + 1)
	    count_rows += 1;

	  if (count_rows == 1)
	    temp = alloc_Array(count_rows + 1, cols);
	  else
	    temp = alloc_Array(count_rows, cols);
	  
	  //cout<<"Pt5 "<<world_rank<< " count_rows = "<<count_rows<<endl;
	  for(int i = 0; i < count_rows; i++)
	    {
	      MPI_Recv(&select_row, 1, MPI_INT, master, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
	      temp[i] = apply_rules(Prime, temp[i], select_row, rows, cols, world_rank);
	      
	    }
	  //cout<<"Pt6 "<<world_rank<<endl;
	  for(int i = 0; i < count_rows; i++)
	    {
	      MPI_Send(temp[i], cols, MPI_INT, master, 0, MPI_COMM_WORLD);
	    }
	  //cout<<"Pt7 "<<world_rank<<endl;
	}
      steps--;
      
    }

  
  
}
