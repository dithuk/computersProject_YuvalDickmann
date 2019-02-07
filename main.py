# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 15:18:39 2019

@author: yuval
"""
import numpy as np
import matplotlib.pyplot as plt

def fit_linear(filename):
    

    # arrange is a dictionary: keys= element's name, fitted values
    def arrangeMethod(data, titles, columns):  
        arrange = {}
        i = 0
        while i < 4:
        # creating valid list for each element
            Variables = []
            specials = []
            current = titles[i]
            #Variables.append(current)
            # Columns have [x,y,dy,dx]   arrange e.g
            if columns:
                start = i
                end = None
                skip = 4
            # Rows have [x....,y....,dy....,dx.....]     arrange e.g     
            else:
                currentIndex= data.index(current)
                start = currentIndex +1 
                location = int(len(data)/4)
                end = start + location -1 
                skip = None
           
                # checking unccertainties > 0
            if current == 'dx' or current == 'dy':
         
                for k in data[start:end:skip]:
                    if float(k) < 0:
                        file_error_zero = "Input file error: Not all unccertainties are positive"
                        return (file_error_zero)
                       
                    else:
                        Variables.append(float(k))
                        if current == 'dy':
                            specials.append((float(k))**2)
                # for X and Y    
            else:
  
                for L in data[start:end:skip]:
                    Variables.append(float(L))  
                    
            arrange[current] = Variables
            i = i +1    
        
        return arrange
        
    def Columns_or_Rows(data):
        columns = False
        try: 
            float(data[3])
        except ValueError:
            columns = True
        return columns    
    

    # weighted mean function
    # thats a general function
    # first input for the function is the list of the requested elements
    # second input is list of y_errs_squared (dy's)
    def weighted_mean (element, err): 
   
        m = 0
        weighted = 0
        sigma_element = 0
        sigma_err = 0
        #divisor = 0
        while m < len(element):
            err_fix = 1/float(err[m])
            current_element = float(element[m])
            sigma_element +=  (current_element * err_fix)
            sigma_err += err_fix
            m += 1
        weighted = sigma_element  / sigma_err
        return  weighted 

    
    # open and read
    file_pointer = open(filename,'r')
    first_data = file_pointer.read()
    
    # mapping the data
    start = first_data.index('axis')-2
    end = first_data.index(']')+1
    x_label =  first_data[start:end]
    y_label =  first_data[end+1:-1]
    
    # new data- fitted without labels 
    data = first_data[:start].lower().split()
    
    # check if columns or rows
    columns = Columns_or_Rows(data)
    
        # 9th first places are argument's names
    
    # checking for lengrh error
    if columns:
        titlesCol = data[:4]
        numbersCol = data[4:]
        if len(numbersCol)/4 != int(len(numbersCol)/4):
                file_error_length = "Input file error: Data lists are not the same length"
                return file_error_length 
        else:
            arrange = arrangeMethod(numbersCol, titlesCol, columns) 

    else:
        location = int(len(data)/4)  # number of points one should have
        titlesRows = []
        for e in data[0::location]:
        
        # each element has to contain same number of argumnents 
        # if the space between each title is not identical 
        # there is an length error
            try:
                float(e)
                file_error_length = "Input file error: Data lists are not the same length"
                return file_error_length
            # creating titles list
            except ValueError:
                titlesRows.append(e)
                
        arrange = arrangeMethod(data, titlesRows, columns)
    

    if type(arrange) == str: 
        return arrange
    
    x = arrange['x']
    y = arrange['y']
    dx = arrange['dx']
    dy = arrange['dy']
    x_squared = [num**2 for num in x]
    dy_squared = [err**2 for err in dy]
    
    def XY (x, y):
        p = 0
        xy = []
        while p < len(x):
            xy.append(x[p]*y[p])
            p = p +1 
        return xy
    
    def numerator(x_squared,x,dy_squared):
        numerator =  weighted_mean(x_squared,dy_squared) - (weighted_mean(x,dy_squared)**2)
        return numerator
    
    def a (yx,y,dy_squared,NN):
        a_iter =(weighted_mean(yx,dy_squared) - (weighted_mean(x,dy_squared)*weighted_mean(y,dy_squared)))
        a = a_iter/NN
        return a
    
    def b (y,dy_squared,x,A):
        b = (weighted_mean(y,dy_squared) - (a* weighted_mean(x,dy_squared)))
        return b
    
    def da (dy_squared,N):
        da_iter = weighted_mean(dy_squared,dy_squared)
        da = da_iter/N * (len(dy_squared))
        return da**(1/2)
    
    def db(dy_squared,x_squared,N):
        db_iter = (weighted_mean(dy_squared,dy_squared) * weighted_mean(x_squared,dy_squared))
        db = db_iter/N * (len(dy_squared))
        return db **(1/2)
    
    def chi2 (y,x,a,b,dy):
        chi2 = 0 
        j = 0
        while j < len(x):
            line = (a*x[j]+b)
            chi2  = chi2 + ((y[j]-line)/(dy[j]))**2
            j += 1
        return chi2
    
    def reduced_chi(chi2, x):
        reduced = len(x)- 2
        
        return chi2/ reduced
    
    
    xy = XY (x, y)
    numerator = numerator(x_squared,x,dy)
    a = a (xy, y, dy_squared,numerator)
    b = b (y, dy_squared, x ,a)
    da= da (dy_squared ,numerator)
    db= db(dy_squared, x_squared, numerator)
    chi2 = chi2 (y,x,a,b,dy)
    chi2_reduced = reduced_chi(chi2, x)
    
    #outputs 
    
    X = np.array(x)
    Y = np.array(y)
    linear = a * X + b
    x_err = np.array(dx)
    y_err = np.array(dy)
    
    plt.errorbar(X, Y, yerr= y_err, xerr= x_err, fmt= 'none', ecolor = 'b')
    plt.plot(X, linear, "r" )  
    plt.xlabel(x_label) 
    plt.ylabel(y_label)
    plt.show()
    plt.savefig("fit_linear.svg")
    print ( 'a =',a, '+-', da, "\n", 'b =', b, '+-' , db , "\n", 'chi2 =', chi2, "\n",'chi2_reduced =', chi2_reduced)
