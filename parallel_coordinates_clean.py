#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 15:05:25 2018

@author: geoff

This script takes a series of CSV data and produces a parallel coordinates
graph split into the top, middle, and bottom thirds of students by final
course grade.

"""
#--- User Inputs --------------------------------------------------
#Which of the state versions are you using?
#Select one of: 3, 6, or 9
stateN = 3

#Input file names for grades and LASSO (cluster data is defined by state)
grade_input_file_name = 'deidentified_course_grades.csv'
lasso_input_file_name = 'ClusterDataMoreStates/lasso.csv'

#Number of total modules
moduleN = 10

#What percentage of students should be highlighted?
Cutoff_Trans = 0.5
Cutoff_Dots  = 0.5

###Pre-script variables and imports#######################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
modules = ['Kinetic Energy', 'Work by a constant force',
           'Work and Kinetic Energy', 'Potential Energy',
           'When is Mechanical Energy Conserved',
           'Simple Application of Conservation of Mechanical Energy',
           'Problems Using Conservation of Mechanical Energy',
           'Problems with Two Types of Potential Energy', 
           'Mechanical Energy and Non-Conservative Work',
           'More mechanical energy problems']

mnames=["m1","m2","m3","m4","m5","m6","m7","m8","m9"]

#Dictionaries to convert from state names to ranking values.
states3_dict={
        'P':3,
        'F':2,
        'A':1
        }
states6_dict={
        'BSP':6,
        'ASP':5,
        'ASF':4,
        'LS' :3,
        'NS' :2,
        'AB' :1
        }
#Note: This is the 'Order1' order.
states9_dict={
        'BSPN':9,
        'ASPN':8,
        'ASPB':7,
        'ASFN':6,
        'LS':5,
        'NS':4,
        'BSPB'  :3,
        'ASFB'  :2,
        'AB'  :1
        }
states9_labels = ["AB","ASFB","BSPB","NS","LS","ASFN",
                       "ASPB","ASPN","BSPN"]
states6_labels = ["AB","NS","LS","ASF","ASP","BSP"]
states3_labels = ["A","F","P"]
tiles=[0,1,2]
tile_name = {0: "Bot",
             1: "Mid",
             2: "Top"}

#Define the variables that differ for different state types.
if stateN == 3:
    states_labels = states3_labels
    states_dict   = states3_dict
    state_input_file_name = 'ClusterDataMoreStates/3states.csv'
    state_num_tag         = "threeStates"
    output_file_name      = "ClusterDataMoreStates/Figures/PCoords3States.pdf"
elif stateN == 6:
    states_labels = states6_labels
    states_dict   = states6_dict
    state_input_file_name = 'ClusterDataMoreStates/6states.csv'
    state_num_tag         = "sixStates"
    output_file_name      = "ClusterDataMoreStates/Figures/PCoords6States.pdf"
elif stateN == 9:
    states_labels = states9_labels
    states_dict   = states9_dict
    state_input_file_name = 'ClusterDataMoreStates/9states.csv'
    state_num_tag         = "nineStates"
    output_file_name      = "ClusterDataMoreStates/Figures/PCoords9States.pdf"
else:
    print("Error: only implemented state numbers are 3, 6, and 9.")


#Pick out the LASSO data for just this module 
lasso_data = pd.read_csv(lasso_input_file_name)
lasso_data = lasso_data[lasso_data['modelNames'] == state_num_tag]
grade_data = pd.read_csv(grade_input_file_name)
df_all = pd.read_csv(state_input_file_name)

#--- Import data sets ----------------------------------------------------
mod_count=1

#List of three lists for storing data of each percentile individually.
Cluster_Data = [[],[],[]]

#Begin by preparing the data

#Subtract 1 from rank for ease of indexing
df_all['rank']=df_all['rank']-1

#Looped for each module
for mname in mnames:
    
    #Look at each percentile of students individually
    for tile in tiles:
        
        #Import the data for this particular file
        #df_clusters contains the data for each student for this module, organized as:
        #  userid:    id for this student
        #  module:    module for this data row
        #  rank:      percentile this student belongs to
        #  order:     ranking for this module
        #  nextOrder: ranking for next module
        #  Cluster:   transition cluster this student belongs to
        
        #Filter frame to just this percentile and module
        df_clusters=df_all[df_all['rank']==tile]
        df_clusters=df_clusters[df_clusters['module']==mname]

        ##Find the mean value of each cluster.
        
        #Number of clusters and consistent order to reference them in
        cluster_numbers=df_clusters['Cluster'].unique()
        
        #Lists to store values for the mean of each cluster. We will combine
        #these into a dataframe after the loop.
        l_cluster_score_means=[]
        l_cluster_nextScore_means =[]
        l_cluster_pop = []
        
        #Go through every cluster and take the mean of 'order' and 'nextOrder.'
        #Then record the population size for this cluster, storing all them
        #in the above lists.
        for group in cluster_numbers:
            df_individ_clust = df_clusters[df_clusters['Cluster']==group]
            
            l_cluster_score_means.append(df_individ_clust.mean()['order'])
            l_cluster_nextScore_means.append(df_individ_clust.mean()['nextOrder'])
            l_cluster_pop.append(len(df_individ_clust.index))
            
        #Combine all lists into dataframe.
        df_clust_data = pd.DataFrame({
                'Cluster': cluster_numbers,
                'Score': l_cluster_score_means,
                'nextScore': l_cluster_nextScore_means,
                'N': l_cluster_pop})
        
        #Store this cluster data away for this percentile in Cluster_Data.
        Cluster_Data[tile].append(df_clust_data)

#End of this loop: all data necessary for plotting found.
        
#--- Cluster Plotting -------------------------------------------------

#Set up figure, ax_list to stores axes, and initialize ax_ind to index the axes.
fig = plt.figure()
fig.set_figheight(10)
fig.set_figwidth(20)
ax_list = []

ax_ind = 0

#For this loop, each row refers to a percentile (Top, Mid, Bot mapping to 3,2,1 respectively)
#and each column to a module, given by moduleN - 1 (we're technically graphing transitions,
#so we only need 9 plots for 10 modules).
for row in np.arange(0,3):
    for col in np.arange(0,moduleN - 1):
        
        #Filter Cluster_Data and df_all to just this module and percentile for plotting
        #clusters and inividual students, respectively.
        clusters=Cluster_Data[row][col]
        students = df_all[(df_all['rank']==tiles[row]) & (df_all['module']==mnames[col])]
        #students=df_all[df_all['rank']==tiles[row]]
        #students=students[students['module']==mnames[col]]
        
        #Number of students per percentile
        GroupSize=clusters['N'].sum(0)
        
        #Sort by cluster size
        sorted_clusters=clusters.sort_values('N',0,False)
        
        #Place this particular axis
        #Each subplot takes up 10% of the figure horizontally and 25% of the
        #figure vertically, with some white space left.
        ax_list.append(fig.add_axes([0.05 + 0.1*col,0.1+0.27*row,.1,.25],xticklabels=[],yticklabels=[],xlim=(0,1),ylim=(0.5,stateN+0.5)))
        
        # Customize the major grid
        ax_list[ax_ind].set_yticks(np.arange(1,stateN+1,step=1))
        ax_list[ax_ind].grid(which='major',axis='y',color='gray',alpha=0.2)
        ax_list[ax_ind].set_axisbelow(True)
        
        # Turn off the display of all ticks.
        ax_list[ax_ind].tick_params(which='both',
                        top='off', # turn off top ticks
                        left='off', # turn off left ticks
                        right='off',  # turn off right ticks
                        bottom='off') # turn off bottom ticks
        
        #If a leftmost-side figure, add labels
        if col == 0:
            ax_list[ax_ind].set_yticklabels(states_labels)
        if row == 0:
            ax_list[ax_ind].text(0.0, -0.1, col+1, horizontalalignment='center',
                   verticalalignment='center', transform=ax_list[ax_ind].transAxes)
            if col == stateN-1:
                ax_list[ax_ind].text(1.0, -0.1, col+2, horizontalalignment='center',
                   verticalalignment='center', transform=ax_list[ax_ind].transAxes) 
        
        #Plot all individual students
        for stu_ind in students.index:
            ax_list[ax_ind].plot([students.at[stu_ind,'order'],students.at[stu_ind,'nextOrder']],
                                     alpha=0.10,
                                     color="#1f77b4",
                                     linewidth=0.6
                                     )
        
        #Starting with the largest cluster, highlight all clusters until
        #at least 50% of students are highlighted.
        Current_Highlight=0
        for clust_ind in sorted_clusters.index:
            if(Current_Highlight < GroupSize*Cutoff_Trans):
                 ax_list[ax_ind].plot([clusters.at[clust_ind,'Score'],clusters.at[clust_ind,'nextScore']],
                                     alpha=0.40,
                                     color="#ff9900",
                                     linewidth=clusters.loc[clust_ind]['N']*0.6
                                     )
                 Current_Highlight+=sorted_clusters.loc[clust_ind]['N']
                                     
            else:
                #Uncomment this area to also plot all other clusters in 
                #a different color.
                """ax_list[ax_ind].plot([clusters.at[clust_ind,'Score'],clusters.at[clust_ind,'nextScore']],
                                     alpha=0.10,
                                     color="#1f77b4",
                                     linewidth=clusters.loc[clust_ind]['N']*0.6)"""
        
        #This section plots the dots for LASSO findings.
        #Begin by filtering to just this module's lasso_data, if any.
        #Then convert to rankings and plot.
        lasso_data_mod = lasso_data[lasso_data["modid"] == mnames[col]]
        for lasso_ind in lasso_data_mod.index:
            lasso_tuple = lasso_data.loc[lasso_ind]
            #If not significant, make it hollow, otherwise it's full.
            if lasso_tuple['p'] > 0.05:
                fill_type='none'
                linestyle = ":"
            else:
                fill_type='full'
                linestyle = "-"
            state_rank = states_dict[lasso_tuple['statename']]
            dot_color = "#7570b3" if lasso_tuple['e'] < 0 else "#1b9e77"
            ax_list[ax_ind].plot([0.001],[state_rank],
                       color=dot_color,
                       fillstyle=fill_type,
                       markersize=7,
                       alpha=0.85,
                       linestyle=linestyle,
                       marker='o')
            ax_list[ax_ind-1].plot([0.999],[state_rank],
                       color=dot_color,
                       fillstyle=fill_type,
                       markersize=7,
                       alpha=0.85,
                       linestyle=linestyle,
                       marker='o')
            
        #Catch for m10, since we'll never actually reach it otherwise. After
        #doing the dots for module 9, do the dots for module 10.
        if col == 8:
            lasso_data_mod = lasso_data[lasso_data["modid"] == 'm10']
            for lasso_ind in lasso_data_mod.index:
                lasso_tuple = lasso_data.loc[lasso_ind]
                #If not significant, make it hollow, otherwise it's full.
                if lasso_tuple['p'] > 0.05:
                    fill_type='none'
                    linestyle = ":"
                else:
                    fill_type='full'
                    linestyle = "-"
                state_rank = states_dict[lasso_tuple['statename']]
                dot_color = "#7570b3" if lasso_tuple['e'] < 0 else "#1b9e77"
                ax_list[ax_ind].plot([0.999],[state_rank],
                           color=dot_color,
                           markersize=7,
                           alpha=0.85,
                           fillstyle=fill_type,
                           linestyle=linestyle,
                           marker='o')
        
        #Now plot the rankings
        
        
        #This plots all "hubs," or just the largest clusters (instead of transitions).
        #Group by nextScore and add all states that end there.
        """stateHubs = sorted_clusters.groupby(['nextScore']).agg(
            {
                 'N':sum,    # Sum duration per group
            }
        ).sort_values('N',ascending=False)
        
        #Plot a dot at largest ending points until over given %.
        Current_Highlight2 = 0
        for state in stateHubs.index:
            if Current_Highlight2 < GroupSize*Cutoff_Dots:
                ax_list[ax_ind].plot([0.99],[state],
                       color="#ff9900",
                       marker='o',
                       linewidth=stateHubs.loc[state]['N']*0.6)
                Current_Highlight2+=stateHubs.loc[state]['N']"""
        
        
        ax_ind=ax_ind+1

#Save and print a message
plt.savefig(output_file_name, bbox_inches='tight', dpi=250)       
plt.close()