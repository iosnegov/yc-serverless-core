# Yandex Cloud Serverless Core

*An educational project demonstrating how to deploy serverless applications on Yandex Cloud.*

> [!WARNING]
> **Project Archived**
> 
> This project is no longer actively maintained. 
> 
> **Context:**  
> Originally, this repository began as a university assignment. Rather than simply completing the task and discarding the code, I chose to expand it into a structured mini-project to deeply explore Yandex Cloud Serverless capabilities. Over time, however, my professional and academic focus has shifted entirely away from Serverless computing.
> 
> **Reason for Archiving:**  
> Consequently, I no longer have an interest in further maintaining this codebase, as my current work no longer involves Serverless architectures. This repository remains available purely as an educational reference for those interested in learning how to structure and deploy basic Serverless applications in Yandex Cloud from scratch.

## Project Structure

```
yc-serverless-core/
├── app/                   # Main application code
├── .env.example           # Example environment variables file
├── pixi.lock              # Locked dependency versions for reproducible environments
├── pixi.toml              # Pixi project configuration: environments, dependencies, 
│                          # platforms and project-specific commands
└── test-deploy.ipynb      # Jupyter notebook for playground testing
```

## Dependencies Overview

| Dependency | Repository | What it is |
| :--- | :--- | :--- |
| **CPython** | [python/cpython](https://github.com/python/cpython) | The de facto standard implementation of the Python programming language. |
| **requests** | [psf/requests](https://github.com/psf/requests) | Widely-used library for making synchronous HTTP requests. |
| **PyJWT** | [jpadilla/pyjwt](https://github.com/jpadilla/pyjwt) | Simple library for encoding and decoding JSON Web Tokens (JWT). |
| **cryptography** | [pyca/cryptography](https://github.com/pyca/cryptography) | Low-level library for secure encryption, signing, hashing, and key management primitives. |
| **boto3** | [boto/boto3](https://github.com/boto/boto3) | Synchronous Python client for Amazon S3 and other AWS services; compatible with S3-compatible storage systems. [^1] |
| **pydantic-settings** | [pydantic/pydantic-settings](https://github.com/pydantic/pydantic-settings) | Pydantic-powered library for managing application configuration and environment variables with strong typing, validation, and seamless `.env` support. |
| **ipykernel** *(Dev)* | [ipython/ipykernel](https://github.com/ipython/ipykernel) | IPython kernel for Jupyter, used for interactive notebook development and local environment testing. |

[^1]: This project uses only synchronous code because Yandex Cloud Functions (like most serverless platforms) handle each request in an isolated, short-lived execution environment. There is no persistent event loop or concurrent request handling, so asynchronous I/O provides no benefit.

## Quick Start

### I. Prerequisites

| Component            | Requirement                               |
| :------------------- | :---------------------------------------- |
| **Package Manager**  | [`Pixi`](https://pixi.prefix.dev/latest/) |
| **Operating System** | GNU/Linux-based system                    |
| **Architecture**     | `x86_64`                                  |

> **Note:**  
> These are not strict requirements, but rather the baseline environment where the code is 
guaranteed to run out of the box. Alternative setups are possible but may require manual 
configuration.

---

### II. Initial Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/snegoviol/yc-serverless-core.git
   cd yc-serverless-core
   ```

2. **Install dependencies**
    
   ```bash
   pixi install --all
   ```

3. **Setup environment configuration**

   ```bash
   pixi run copy-env
   ```

---

### III. Cloud Environment Preparation

---

#### i. Create a Folder

1. Go to the [Clouds page](https://console.yandex.cloud/clouds).
2. Find your cloud in the list and click the `three-dot menu` next to its name.
3. Select `Create folder`.
4. Enter a name for the folder.
5. Click `Create`.

---

#### ii. Create a Service Account

1. Find your folder in the list and click the `three-dot menu` next to its name.
2. Select `Create service account`.
3. Enter a name for the service account.
4. Click `Create`.

---

#### iii. Assign Required Roles to the Service Account

1. Find your folder in the list and click the `three-dot menu` next to its name.
2. Select `Access bindings`.
3. Click `Configure access`.
4. In the window that opens, select `Service accounts`.
5. Select your service account from the list.
6. Click `Add role` and assign **all** of the following roles: [^2]
   - `iam.admin` — to allow the service account to generate IAM tokens for itself.
   - `storage.admin` — to create and manage Object Storage buckets and objects.
   - `lockbox.admin` — to create and manage Lockbox secrets.
   - `functions.admin` — to create and manage Cloud Functions.
   - `apigateway.admin` — to create, update, and retrieve API Gateway resources.
7. Click `Save`.

[^2]: Granting broad administrative roles (`*.admin`) to a single service account violates the principle of least privilege, which recommends granting only the minimum permissions necessary for a specific task. However, for the purposes of this educational project, where simplicity is prioritized over production-grade security, a single service account with consolidated admin permissions is used to reduce configuration complexity.

---

#### iv. Create an Authorized Key for the Service Account

1. In the management console, make sure you’re in the correct folder.
2. In the folder services list, find and click `Identity and Access Management`.
3. Find and click on your service account.
4. Find and click `Create new key`.
5. Click `Create authorized key`.
6. Choose your preferred encryption algorithm.
7. Click `Create`.
8. Click `Download file with keys`.
9. Save the downloaded key file to your project directory and set its path as the `YC_AUTHORIZED_KEY` environment variable.

---

#### v. Obtain the Folder ID

1. Go to the [Folders page](https://console.yandex.cloud/folders).
2. Find your folder in the list and click its name.
3. In the browser’s address bar, locate the URL. It will look like:  
   `https://console.yandex.cloud/folders/b1gabc123def456ghi7`
4. The string after `/folders/` (e.g., `b1gabc123def456ghi7`) is your **Folder ID**.
5. Copy this ID and set it as the `YC_FOLDER_ID` environment variable.

---

#### vi. Create Static Access Keys for Object Storage

1. In the management console, make sure you’re in the correct folder.
2. In the folder services list, find and click `Identity and Access Management`.
3. Find and click on your service account.
4. Find and click `Create new key`.
5. Click `Create static access key`.
6. Click **Create**.
7. Copy the data and set `Key ID` as the `S3_ACCESS_KEY` environment variable and `Your secret key` as the `S3_SECRET_KEY` environment variable.

---

#### vii. Obtain the Service Account ID

1. In the management console, make sure you’re in the correct folder.
2. In the folder services list, find and click `Identity and Access Management`.
3. Find and click on your service account.
4. On the service account details page, locate the **ID** field. It will look like:  
   `aje12abc34def56ghi78jkl90mno`
5. Copy this ID and set it as the `YC_SERVICE_ACCOUNT_ID` environment variable.

---

### III. Testing

Once the environment is set up, you can run and test the serverless backend using the interactive Jupyter notebook `test-deploy.ipynb`. It demonstrates the full workflow — including backend deployment and all REST API endpoints.

## License

Each file in this repository is licensed under the [MIT No Attribution License](LICENSE.txt).
