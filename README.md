# build notes:
- it works in dev running on a physical android device. just some buttons etc need to be made responsive. The map doesn't work on the physical device so need to check out the license or alternatives.
- Codemagic builds it to production as an aab rather than apk

# External Services used
- Firebase Authentication
- Frontend deployed on CodeMagic.io
- Express.js api hosted on Render
- Data and ML on Azure


# How the app uses its databases
The Application has two databases, both in Azure. One SQL for user data, club data and game bookings. The other is a JsonLines document strictly of game bookings in Blob Storage, consumed by the ML.

(_This is because at the time of research ML preferred to consume Documents instead of SQL, and SQL was an effective solution for potentially relational user and club data etc_)

The SQL table for games_data **must** remain consistent with the JsonLines document MOCK_GAME_DATA.jsonl for the ML to work effectively.

This is achieved in-app by calling separate services simultaneously. One for SQL, one for Blob Storage.
![uml](https://github.com/TortoiseLeaf/MG_docs/blob/main/Media/DBs_UML.png?raw=true)

When the user books or updates a game booking, methods like these fire together. You'll find them mostly in `/service`

(With the exception of `create_game_page.dart` and `recs_game_list.dart`)

<br />

# How the app consumes the ML results
The ML is run manually from Azure ML Studio (see [here](https://github.com/TortoiseLeaf/MG_docs/blob/main/ML/AZURE_ML_DOCS.docx) for running the model). It's accessed and consumed by the frontend like an API.

In `components/recs_game_list.dart` the Blob is accessed using the Blob connection string, and Blob file path. The MLResults file is parsed as a CSV and the id for each recommended game is extracted into a list, by user.

That list is then matched to the SQL games, and the component renders these into a games list.

<br />

# Connecting to the Azure Databases
The Azure Blob connection string and other env vars are saved locally in `assets/.env.development`. The file is included in the .gitignore and the env vars are stored in the CodeMagic deployment workflow.

The connection string can also be accessed from the Azure portal using this method [here](https://learn.microsoft.com/en-us/answers/questions/1071173/where-can-i-find-storage-account-connection-string).

The Azure SQL db is accessed using the `mb_node` express api, which uses a `checkAuthentication` middleware to check for a firebase auth token before allowing access.

<br />

# Recreating the ML Pipeline
From the Designer in Azure ML Studio, click "Create a new pipeline using
classic prebuilt components" and select the Restaurant Ratings Wide and Deep Recommendation model. Add and remove prebuilt components to match the pipeline shown below. 

Custom Data sources need to be added as components like users_sql and mock_game_data.jsonl, you can learn more [here](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-component-pipelines-ui?view=azureml-api-2).

![pipeline](https://github.com/TortoiseLeaf/MG_docs/blob/main/ML/Pipeline_setup.png?raw=true)

Double click the components in the pipeline to adjust their settings according to what's written in the image above. The Execute_Python_Script for extracting all user ids from each game can be found [here](https://github.com/TortoiseLeaf/MG_docs/blob/main/ML/Execute_python_script.py)

Refer to [AZURE_ML_DOCS.docx](https://github.com/TortoiseLeaf/MG_docs/blob/main/ML/AZURE_ML_DOCS.docx) for more information.

<br />

# ML Data resiliency in the Frontend
To ensure the SQL and Blob remain consistent with each other:
- the blob update function is only called if the SQL request returns a status code of 200
- if the blob update is unsuccessful and returns a `blobUpdated = false;`, the SQL request is rolled back.


```
updateGameBooking() {

  // SQL request is made

	if (response.statusCode == 200) {
	
		bool blobUpdated = await updateBlob()
	
		if(blobUpdated) {
		showDialog("successful")
		}
	
		if(!blobUpdated) {

		// rollback SQL transaction

		showDialog("unsuccessful")
		}
	}
}
```
<br />

# Considerations
It could be pertinent to use just one type of db for both users and ML for both consistency and performance. In the case of Azure ML Studio at the time of writing, the ML designer only accepts Azure Blob files as a noSQL alternative to SQL, which has its limiations.

Pros of using only SQL:
-  Easier to keep data consistent
-  Easier to manage data in-app
-  Blob data can be unruly to maintain compared to SQL
-  No need for separate game dbs

Cons of only SQL:
- Less scalable than document dbs
- ML generally prefers to consume documents (could affect long term efficiacy)

