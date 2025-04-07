# PLUS_softwaredev_2025_rabina

## Assignment 2

1. The task was done in MacOS with the conda version 24.7.1 installed.

   <img width="543" alt="conda_v" src="https://github.com/user-attachments/assets/80472201-56a3-467b-bd0b-909232a8add2" />





3. The given [repository](https://github.com/augustinh22/geo-software-dev/tree/main) was cloned. Terminal was opened and navigated to the directory where the repository was cloned.

    <img width="543" alt="dir" src="https://github.com/user-attachments/assets/5846fd47-3883-4eb5-be64-e1d15d7c69a8" />




3. The following command was executed to create the first environment based on 'software_dev_v1.yml' file.

    ```
   conda env create -f software_dev_v1.yml
    ```

   Since, it is an windows operating system dependent environment, the following error occured when executed on Mac OS.

    <img width="615" alt="Screenshot 2568-04-07 at 12 18 02" src="https://github.com/user-attachments/assets/397abcdd-fb32-4685-8605-44839d0fa8c5" />

    <img width="615" alt="Screenshot 2568-04-07 at 12 19 10" src="https://github.com/user-attachments/assets/cc5e4297-6a61-47a5-98a2-f2ecca0a8043" />



5. Similarly, the following command was executed to create the second environment based on 'software_dev_v2.yml' file.

    ```
   conda env create -f software_dev_v2.yml
   ```

    The name of environment is the value assigned to the "name" key in respective .yml file. In this case, it is software_dev_v2.
   
     <img width="452" alt="Screenshot 2568-04-07 at 21 19 27" src="https://github.com/user-attachments/assets/4693cb5f-5ae2-405a-a3a4-5f10717e85d7" />

     Since it is the generic one, the environment was created successfully as shown below. 

    <img width="650" alt="conda2" src="https://github.com/user-attachments/assets/66933d08-fa16-44fe-ada9-9e141d7e7dd0" />

4. Finally, the environment was activated using following command:

    <pre> conda activate software_dev_v1.yml </pre>
